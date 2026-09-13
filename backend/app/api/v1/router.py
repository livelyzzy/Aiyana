"""v1 路由聚合。"""
from fastapi import APIRouter

from app.api.v1 import auth, evaluations, inspections, reports, submissions, tasks, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(tasks.router)
api_router.include_router(submissions.router)
api_router.include_router(inspections.router)
api_router.include_router(evaluations.router)
api_router.include_router(reports.router)
