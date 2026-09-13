"""报表相关 Schema。"""
from pydantic import BaseModel


class ReportRequest(BaseModel):
    """导出报表请求。"""

    submission_id: int | None = None  # 学生单份报告
    task_id: int | None = None  # 课程/班级维度统计
    format: str = "xlsx"  # xlsx | pdf
