"""评价路由：评价指标管理、AI 评分、教师主观评分。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.evaluation import EvaluationRubric, Score
from app.models.training import Submission
from app.models.user import User
from app.schemas.evaluation import EvaluationResult, RubricCreate, RubricOut, ScoreOut, ScoreUpdate
from app.services.evaluation import compute_total, run_ai_evaluation

router = APIRouter(tags=["评价管理"])


# ---------------- 评价指标 ----------------
@router.post("/rubrics", response_model=RubricOut, status_code=201)
async def create_rubric(
    payload: RubricCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> EvaluationRubric:
    rubric = EvaluationRubric(**payload.model_dump())
    db.add(rubric)
    await db.commit()
    await db.refresh(rubric)
    return rubric


@router.get("/rubrics", response_model=list[RubricOut])
async def list_rubrics(
    task_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[EvaluationRubric]:
    stmt = select(EvaluationRubric).order_by(EvaluationRubric.id)
    if task_id is not None:
        stmt = stmt.where(
            (EvaluationRubric.task_id == task_id) | (EvaluationRubric.task_id.is_(None))
        )
    result = await db.scalars(stmt)
    return list(result)


@router.put("/rubrics/{rubric_id}", response_model=RubricOut)
async def update_rubric(
    rubric_id: int,
    payload: RubricCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> EvaluationRubric:
    rubric = await db.get(EvaluationRubric, rubric_id)
    if rubric is None:
        raise HTTPException(404, "指标不存在")
    for key, value in payload.model_dump().items():
        setattr(rubric, key, value)
    await db.commit()
    await db.refresh(rubric)
    return rubric


@router.delete("/rubrics/{rubric_id}", status_code=204)
async def delete_rubric(
    rubric_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> None:
    rubric = await db.get(EvaluationRubric, rubric_id)
    if rubric is None:
        raise HTTPException(404, "指标不存在")
    await db.delete(rubric)
    await db.commit()


# ---------------- 评分 ----------------
@router.post("/submissions/{submission_id}/evaluate")
async def evaluate_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> EvaluationResult:
    submission = await db.get(Submission, submission_id)
    if submission is None:
        raise HTTPException(404, "成果不存在")

    rubrics = list(
        await db.scalars(
            select(EvaluationRubric).where(
                (EvaluationRubric.task_id == submission.task_id)
                | (EvaluationRubric.task_id.is_(None))
            )
        )
    )
    if not rubrics:
        raise HTTPException(400, "尚未配置评价指标，请先创建指标")

    rubric_dicts = [
        {"id": r.id, "name": r.name, "description": r.description, "weight": r.weight}
        for r in rubrics
    ]
    ai_items = await run_ai_evaluation(rubric_dicts, submission.parsed_content)
    by_name = {r.name: r for r in rubrics}

    # 删除旧评分，重新生成
    for old in await db.scalars(select(Score).where(Score.submission_id == submission_id)):
        await db.delete(old)

    created: list[Score] = []
    for item in ai_items:
        rubric = by_name.get(item.get("name", ""))
        if rubric is None:
            continue
        try:
            score_val = float(item.get("score", 0))
        except (TypeError, ValueError):
            score_val = 0.0
        score = Score(
            submission_id=submission_id,
            rubric_id=rubric.id,
            ai_score=min(max(score_val, 0), 100),
            comment=item.get("comment"),
        )
        db.add(score)
        created.append(score)

    submission.status = "evaluated"
    await db.commit()
    for s in created:
        await db.refresh(s)

    items_out = [ScoreOut.model_validate(s) for s in created]
    total = compute_total([s.__dict__ for s in created], rubric_dicts)
    return EvaluationResult(submission_id=submission_id, total_score=total, items=items_out)


@router.get("/submissions/{submission_id}/scores", response_model=list[ScoreOut])
async def list_scores(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Score]:
    result = await db.scalars(select(Score).where(Score.submission_id == submission_id))
    return list(result)


@router.put("/scores/{score_id}", response_model=ScoreOut)
async def adjust_score(
    score_id: int,
    payload: ScoreUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> Score:
    """教师主观评分入口：调整分数或补充评语。"""
    score = await db.get(Score, score_id)
    if score is None:
        raise HTTPException(404, "评分记录不存在")
    if payload.teacher_score is not None:
        score.teacher_score = payload.teacher_score
    if payload.comment is not None:
        score.comment = payload.comment
    await db.commit()
    await db.refresh(score)
    return score


@router.get("/submissions/{submission_id}/result")
async def get_result(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> dict:
    scores = list(
        await db.scalars(select(Score).where(Score.submission_id == submission_id))
    )
    rubrics = list(await db.scalars(select(EvaluationRubric)))
    rubric_dicts = [
        {"id": r.id, "name": r.name, "weight": r.weight} for r in rubrics
    ]
    score_dicts = [
        {
            "rubric_id": s.rubric_id,
            "ai_score": s.ai_score,
            "teacher_score": s.teacher_score,
        }
        for s in scores
    ]
    total = compute_total(score_dicts, rubric_dicts)
    return {
        "submission_id": submission_id,
        "total_score": total,
        "items": [ScoreOut.model_validate(s) for s in scores],
    }
