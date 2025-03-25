import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.user import User


@pytest.mark.asyncio
async def test_read_user(async_session):
    # GIVEN: 여러 사용자 생성
    users = [
        User(name=f"user{i}", password=f"password{i}", email=f"user{i}@example.com")
        for i in range(15)
    ]
    async_session.add_all(users)
    await async_session.commit()

    # WHEN: 사용자 목록 조회 API 호출
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/v1/users/list")

        # THEN: 응답 검증
        assert response.status_code == 200
        assert len(response.json()) == 15
