"""评价指标与评分模型。"""
from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class EvaluationRubric(Base, TimestampMixin):
    """评价指标（维度）及权重：可绑定具体任务，也可作为全局通用指标。"""

    __tablename__ = "evaluation_rubrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("training_tasks.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)  # 如「代码质量」
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    weight: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)


class Score(Base, TimestampMixin):
    """评分记录：AI 客观分 + 教师主观分 + 可解释性评语。"""

    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    rubric_id: Mapped[int] = mapped_column(ForeignKey("evaluation_rubrics.id"), nullable=False)
    ai_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    teacher_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
