"""智能核查结果模型。"""
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class InspectionResult(Base, TimestampMixin):
    """对某份成果的智能核查结果（JSON 存储结构化发现）。"""

    __tablename__ = "inspection_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("submissions.id"), nullable=False)
    result_json: Mapped[str] = mapped_column(Text, nullable=False)  # 偏离项/逻辑漏洞/步骤完整性
    overall: Mapped[str] = mapped_column(Text, nullable=False, default="")
