import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base
from app.config import settings
from app.api.dependencies import get_db


@pytest.fixture(scope="function")
async def async_session():
    # SQLite 메모리 데이터베이스 사용 (테스트마다 초기화)
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 테스트 세션 생성
    TestAsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # 테스트 후 데이터베이스 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
def override_get_async_session(async_session):
    async def _override_get_async_session():
        yield async_session

    app.dependency_overrides[get_db] = _override_get_async_session
