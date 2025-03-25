import pytest

from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_async_read_main(async_session):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/docs")
        assert response.status_code == 200
