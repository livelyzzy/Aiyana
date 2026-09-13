"""实训任务与实训成果模型。"""
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class TrainingTask(Base, TimestampMixin):
    """实训任务：教师发布的任务及验收要求。"""

    __tablename__ = "training_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    course_name: Mapped[str] = mapped_column(String(128), nullable=False, default="软件实训")
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    requirements: Mapped[str] = mapped_column(Text, nullable=False, default="")
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="task")


class Submission(Base, TimestampMixin):
    """实训成果：学生/小组上传的成果及其解析结果。"""

    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("training_tasks.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="uploaded", nullable=False)
    # uploaded -> parsing -> parsed -> inspected -> evaluated -> failed
    file_names: Mapped[str] = mapped_column(Text, nullable=False, default="")  # 逗号分隔
    parsed_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    task: Mapped[TrainingTask] = relationship(back_populates="submissions")
