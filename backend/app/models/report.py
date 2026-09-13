"""报表记录模型。"""
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class Report(Base, TimestampMixin):
    """导出的报表记录（学生单份 / 班级/课程统计）。"""

    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    report_type: Mapped[str] = mapped_column(String(32), nullable=False)  # student | class
    target: Mapped[str] = mapped_column(String(128), nullable=False, default="")  # 学生名/班级名
    format: Mapped[str] = mapped_column(String(8), nullable=False, default="xlsx")  # xlsx | pdf
    file_path: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
