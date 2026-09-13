"""实训任务与成果相关 Schema。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TrainingTaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=256)
    course_name: str = "软件实训"
    description: str = ""
    requirements: str = ""
    deadline: datetime | None = None


class TrainingTaskCreate(TrainingTaskBase):
    pass


class TrainingTaskUpdate(BaseModel):
    title: str | None = None
    course_name: str | None = None
    description: str | None = None
    requirements: str | None = None
    deadline: datetime | None = None


class TrainingTaskOut(TrainingTaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    teacher_id: int
    created_at: datetime


class SubmissionCreate(BaseModel):
    task_id: int
    group_name: str | None = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: int
    student_id: int
    group_name: str | None
    status: str
    file_names: str
    parsed_content: str | None
    parse_error: str | None
    created_at: datetime
