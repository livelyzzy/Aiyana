"""初始化数据库：建表 + 写入种子数据（默认教师/学生账号）。"""
import asyncio

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import async_session_factory, engine
from app.models.user import User


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_users() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalars().first() is not None:
            return

        defaults = [
            User(
                username="teacher",
                hashed_password=hash_password("teacher123"),
                full_name="示例教师",
                role="teacher",
            ),
            User(
                username="student",
                hashed_password=hash_password("student123"),
                full_name="示例学生",
                role="student",
            ),
        ]
        session.add_all(defaults)
        await session.commit()


async def init_db() -> None:
    await create_tables()
    await seed_users()


if __name__ == "__main__":
    asyncio.run(init_db())
    print("数据库初始化完成。默认账号：teacher/teacher123，student/student123")
