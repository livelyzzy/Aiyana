"""实训任务路由。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_role
from app.db.session import get_db
from app.models.training import TrainingTask
from app.models.user import User
from app.schemas.training import TrainingTaskCreate, TrainingTaskOut, TrainingTaskUpdate

router = APIRouter(prefix="/tasks", tags=["实训任务"])


@router.post("", response_model=TrainingTaskOut, status_code=201)
async def create_task(
    payload: TrainingTaskCreate,
    db: AsyncSession = Depends(get_db),
    teacher: User = Depends(require_role("teacher")),
) -> TrainingTask:
    task = TrainingTask(**payload.model_dump(), teacher_id=teacher.id)
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.get("", response_model=list[TrainingTaskOut])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[TrainingTask]:
    result = await db.scalars(select(TrainingTask).order_by(TrainingTask.id.desc()))
    return list(result)


@router.get("/{task_id}", response_model=TrainingTaskOut)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
) -> TrainingTask:
    task = await db.get(TrainingTask, task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")
    return task


@router.put("/{task_id}", response_model=TrainingTaskOut)
async def update_task(
    task_id: int,
    payload: TrainingTaskUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> TrainingTask:
    task = await db.get(TrainingTask, task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, key, value)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_role("teacher")),
) -> None:
    task = await db.get(TrainingTask, task_id)
    if task is None:
        raise HTTPException(404, "任务不存在")
    await db.delete(task)
    await db.commit()
