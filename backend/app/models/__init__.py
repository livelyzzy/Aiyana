"""数据模型统一导出，便于 Base.metadata 收集所有表。"""
from app.models.evaluation import EvaluationRubric, Score
from app.models.inspection import InspectionResult
from app.models.report import Report
from app.models.training import Submission, TrainingTask
from app.models.user import User

__all__ = [
    "User",
    "TrainingTask",
    "Submission",
    "EvaluationRubric",
    "Score",
    "InspectionResult",
    "Report",
]
