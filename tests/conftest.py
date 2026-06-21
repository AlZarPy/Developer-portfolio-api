import asyncio
import os
from pathlib import Path

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./data/test.db"
os.environ["AI_PROVIDER"] = "mock"
os.environ["EMAIL_ENABLED"] = "false"
os.environ["CONTACT_RATE_LIMIT"] = "2/minute"
os.environ["CORS_ORIGINS"] = "http://testserver"
os.environ["LOG_FILE"] = "logs/test.log"

import pytest
from fastapi.testclient import TestClient

from app.db.database import Base, engine
from app.main import app


async def reset_test_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)


@pytest.fixture()
def client() -> TestClient:
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    asyncio.run(reset_test_database())

    storage = app.state.limiter._storage
    reset = getattr(storage, "reset", None)
    if callable(reset):
        reset()

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def contact_payload() -> dict[str, str | None]:
    return {
        "name": "Maria Client",
        "email": "maria@example.com",
        "phone": "+995 555 11 22 33",
        "message": "I need a FastAPI backend for a new project with PostgreSQL.",
        "source": "website",
    }
