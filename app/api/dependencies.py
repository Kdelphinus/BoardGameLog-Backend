from app.db.session import AsyncSessionLocal, RedisClient


# 의존성 주입을 위한 세션 생성 함수
async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e
    except Exception as e:
        raise e  # 데이터베이스 연결 실패 등의 처리


async def get_redis():
    try:
        yield RedisClient  # FastAPI의 Dependency Injection을 통해 사용
    finally:
        await RedisClient.close()
