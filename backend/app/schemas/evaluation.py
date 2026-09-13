"""评价指标与评分相关 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RubricCreate(BaseModel):
    task_id: int | None = None
    name: str = Field(min_length=1, max_length=128)
    description: str = ""
    weight: float = Field(default=1.0, gt=0)


class RubricOut(RubricCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class ScoreUpdate(BaseModel):
    teacher_score: float | None = Field(default=None, ge=0, le=100)
    comment: str | None = None


class ScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    rubric_id: int
    ai_score: float | None
    teacher_score: float | None
    comment: str | None


class EvaluationResult(BaseModel):
    """一次评价的整体结果，供前端展示。"""

    submission_id: int
    total_score: float
    items: list[ScoreOut]
