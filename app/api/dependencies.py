from app.db.session import AsyncSessionLocal


# 의존성 주입을 위한 세션 생성 함수
async def get_db():
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise
    except Exception as e:
        raise  # 데이터베이스 연결 실패 등의 처리
