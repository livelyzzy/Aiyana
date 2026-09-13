"""报表路由：生成并导出学生单份报告 / 课程班级统计报表。"""
import json
import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.core.config import settings
from app.db.session import get_db
from app.models.evaluation import EvaluationRubric, Score
from app.models.inspection import InspectionResult
from app.models.report import Report
from app.models.training import Submission, TrainingTask
from app.models.user import User
from app.schemas.report import ReportRequest
from app.services.evaluation import compute_total
from app.services.report import to_excel, to_pdf

router = APIRouter(prefix="/reports", tags=["报表"])


async def _score_dicts(db: AsyncSession, submission_id: int) -> list[dict]:
    scores = await db.scalars(select(Score).where(Score.submission_id == submission_id))
    return [
        {
            "rubric_id": s.rubric_id,
            "ai_score": s.ai_score,
            "teacher_score": s.teacher_score,
        }
        for s in scores
    ]


async def _rubric_dicts(db: AsyncSession) -> list[dict]:
    rubrics = await db.scalars(select(EvaluationRubric))
    return [{"id": r.id, "name": r.name, "weight": r.weight} for r in rubrics]


async def _total(db: AsyncSession, submission_id: int) -> float:
    return compute_total(await _score_dicts(db, submission_id), await _rubric_dicts(db))


def _build_student_payload(
    submission: Submission, task: TrainingTask, student: User, scores: list[Score], rubrics: list[EvaluationRubric]
) -> dict:
    name_map = {r.id: r.name for r in rubrics}
    rubric_list = [{"id": r.id, "name": r.name, "weight": r.weight} for r in rubrics]
    score_dicts = [
        {
            "rubric_id": s.rubric_id,
            "ai_score": s.ai_score,
            "teacher_score": s.teacher_score,
        }
        for s in scores
    ]
    total = compute_total(score_dicts, rubric_list)

    labels = [name_map.get(s.rubric_id, f"指标{s.rubric_id}") for s in scores]
    values = [
        round(s.teacher_score if s.teacher_score is not None else (s.ai_score or 0), 1)
        for s in scores
    ]

    return {
        "title": f"实训评价报告 - {student.full_name}",
        "meta": [
            ("学生", student.full_name),
            ("任务", task.title),
            ("课程", task.course_name),
            ("总分", total),
        ],
        "sections": [
            {
                "name": "分项评分",
                "headers": ["评价指标", "权重", "AI 评分", "教师评分", "评语"],
                "rows": [
                    [
                        name_map.get(s.rubric_id, "未知"),
                        next((r.weight for r in rubrics if r.id == s.rubric_id), 1),
                        s.ai_score if s.ai_score is not None else "-",
                        s.teacher_score if s.teacher_score is not None else "-",
                        s.comment or "",
                    ]
                    for s in scores
                ],
            }
        ],
        "charts": [{"title": "能力雷达图", "type": "radar", "labels": labels, "values": values}]
        if labels
        else [],
    }


def _build_class_payload(task: TrainingTask, rows: list[tuple[str, float]]) -> dict:
    names = [r[0] for r in rows]
    totals = [r[1] for r in rows]
    return {
        "title": f"课程统计报表 - {task.course_name}",
        "meta": [
            ("任务", task.title),
            ("课程", task.course_name),
            ("提交人数", len(rows)),
            ("平均分", round(sum(totals) / len(totals), 2) if totals else 0),
        ],
        "sections": [
            {
                "name": "成绩汇总",
                "headers": ["学生", "总分"],
                "rows": [[n, t] for n, t in rows],
            }
        ],
        "charts": [{"title": "成绩分布", "type": "bar", "labels": names, "values": totals}]
        if names
        else [],
    }


@router.post("/export")
async def export_report(
    req: ReportRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> Response:
    if req.format not in ("xlsx", "pdf"):
        raise HTTPException(400, "仅支持 xlsx / pdf 格式")

    rubrics = list(await db.scalars(select(EvaluationRubric)))

    if req.submission_id is not None:
        submission = await db.get(Submission, req.submission_id)
        if submission is None:
            raise HTTPException(404, "成果不存在")
        task = await db.get(TrainingTask, submission.task_id)
        student = await db.get(User, submission.student_id)
        scores = list(
            await db.scalars(select(Score).where(Score.submission_id == submission.id))
        )
        payload = _build_student_payload(submission, task, student, scores, rubrics)
        report_type, target = "student", student.full_name
        fname = f"report_student_{student.username}_{submission.id}"
    elif req.task_id is not None:
        task = await db.get(TrainingTask, req.task_id)
        if task is None:
            raise HTTPException(404, "任务不存在")
        submissions = list(
            await db.scalars(select(Submission).where(Submission.task_id == task.id))
        )
        rows: list[tuple[str, float]] = []
        for sub in submissions:
            student = await db.get(User, sub.student_id)
            rows.append((student.full_name if student else f"用户{sub.student_id}", await _total(db, sub.id)))
        payload = _build_class_payload(task, rows)
        report_type, target = "class", task.course_name
        fname = f"report_class_{task.id}"
    else:
        raise HTTPException(400, "请指定 submission_id（学生报告）或 task_id（班级统计）")

    content = to_excel(payload) if req.format == "xlsx" else to_pdf(payload)
    media = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if req.format == "xlsx"
        else "application/pdf"
    )

    # 持久化报表文件与记录
    report_dir = Path(settings.report_dir)
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / f"{fname}_{datetime.now():%Y%m%d_%H%M%S}.{req.format}"
    path.write_bytes(content)
    db.add(
        Report(
            report_type=report_type,
            target=target,
            format=req.format,
            file_path=str(path),
            data_json=json.dumps(payload, ensure_ascii=False),
        )
    )
    await db.commit()

    return Response(
        content=content,
        media_type=media,
        headers={"Content-Disposition": f'attachment; filename="{path.name}"'},
    )


@router.get("")
async def list_reports(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> list[dict]:
    reports = await db.scalars(select(Report).order_by(Report.id.desc()))
    return [
        {
            "id": r.id,
            "report_type": r.report_type,
            "target": r.target,
            "format": r.format,
            "file_path": os.path.basename(r.file_path),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in reports
    ]
