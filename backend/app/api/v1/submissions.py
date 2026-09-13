"""实训成果路由：上传、解析、结构化抽取。"""
import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db
from app.models.training import Submission, TrainingTask
from app.models.user import User
from app.schemas.training import SubmissionOut
from app.services.llm.base import LLMError
from app.services.parsing.dispatcher import SUPPORTED_EXTENSIONS, extract_text
from app.services.structuring import structure_content

router = APIRouter(prefix="/submissions", tags=["实训成果"])


async def _save_upload(file: UploadFile, sub_dir: Path) -> str:
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"不支持的文件类型：{ext or '未知'}")
    name = f"{uuid.uuid4().hex}{ext}"
    dest = sub_dir / name
    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(413, f"文件超过大小限制（{settings.max_upload_size_mb}MB）")
    dest.write_bytes(content)
    return str(dest)


@router.post("", response_model=SubmissionOut, status_code=201)
async def upload_submission(
    task_id: int = Form(...),
    group_name: str | None = Form(default=None),
    files: list[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    student: User = Depends(get_current_user),
) -> Submission:
    task = await db.get(TrainingTask, task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")

    sub_dir = Path(settings.upload_dir) / str(task_id)
    sub_dir.mkdir(parents=True, exist_ok=True)

    saved_paths: list[str] = []
    try:
        for f in files:
            saved_paths.append(await _save_upload(f, sub_dir))
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"文件保存失败：{exc}") from exc

    submission = Submission(
        task_id=task_id,
        student_id=student.id,
        group_name=group_name,
        file_names=",".join(os.path.basename(p) for p in saved_paths),
        status="parsing",
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    try:
        raw_parts = [extract_text(p) for p in saved_paths]
        raw_text = "\n\n".join(p for p in raw_parts if p)
        structured = await structure_content(raw_text)
        submission.parsed_content = json.dumps(structured, ensure_ascii=False)
        submission.status = "parsed"
    except LLMError as exc:
        submission.status = "failed"
        submission.parse_error = f"结构化解析失败：{exc}"
    except Exception as exc:  # noqa: BLE001
        submission.status = "failed"
        submission.parse_error = f"解析失败：{exc}"

    await db.commit()
    await db.refresh(submission)
    return submission


@router.get("", response_model=list[SubmissionOut])
async def list_submissions(
    task_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> list[Submission]:
    stmt = select(Submission).order_by(Submission.id.desc())
    if task_id is not None:
        stmt = stmt.where(Submission.task_id == task_id)
    elif user.role == "student":
        stmt = stmt.where(Submission.student_id == user.id)
    result = await db.scalars(stmt)
    return list(result)


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Submission:
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, "成果不存在")
    return submission


@router.post("/{submission_id}/parse", response_model=SubmissionOut)
async def reparse_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> Submission:
    """对已上传成果重新执行解析（文件需仍存在）。"""
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, "成果不存在")
    task = await db.get(TrainingTask, submission.task_id)
    paths = [
        str(Path(settings.upload_dir) / str(task.id) / name)
        for name in submission.file_names.split(",")
        if name
    ]
    try:
        raw_text = "\n\n".join(extract_text(p) for p in paths if os.path.exists(p))
        submission.parsed_content = json.dumps(
            await structure_content(raw_text), ensure_ascii=False
        )
        submission.status = "parsed"
        submission.parse_error = None
    except Exception as exc:  # noqa: BLE001
        submission.status = "failed"
        submission.parse_error = str(exc)
    await db.commit()
    await db.refresh(submission)
    return submission
