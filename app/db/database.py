from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str | None = None) -> AsyncEngine:
    settings = get_settings()
    url = database_url or settings.database_url
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}

    return create_async_engine(
        url,
        echo=settings.debug,
        pool_pre_ping=not url.startswith("sqlite"),
        connect_args=connect_args,
    )


engine = build_engine()
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def create_database_schema(current_engine: AsyncEngine | None = None) -> None:
    from app.db import models  # noqa: F401

    target_engine = current_engine or engine
    async with target_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
