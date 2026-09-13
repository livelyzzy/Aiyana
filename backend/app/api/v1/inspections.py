"""智能核查路由。"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.inspection import InspectionResult
from app.models.training import Submission, TrainingTask
from app.models.user import User
from app.services.inspection import run_inspection

router = APIRouter(prefix="/submissions", tags=["智能核查"])


@router.post("/{submission_id}/inspect")
async def inspect_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, "成果不存在")
    task = await db.get(TrainingTask, submission.task_id)
    if task is None:
        raise HTTPException(404, "关联任务不存在")

    result = await run_inspection(task.requirements, submission.parsed_content)
    submission.status = "inspected"

    record = await db.scalar(
        select(InspectionResult).where(InspectionResult.submission_id == submission_id)
    )
    if record is None:
        record = InspectionResult(submission_id=submission_id, result_json="{}")
        db.add(record)
    record.result_json = json.dumps(result, ensure_ascii=False)
    record.overall = result.get("overall", "")
    await db.commit()
    return result


@router.get("/{submission_id}/inspection")
async def get_inspection(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    record = await db.scalar(
        select(InspectionResult).where(InspectionResult.submission_id == submission_id)
    )
    if record is None:
        return {
            "deviations": [],
            "logic_issues": [],
            "missing_steps": [],
            "overall": "尚未执行核查。",
        }
    return json.loads(record.result_json)
