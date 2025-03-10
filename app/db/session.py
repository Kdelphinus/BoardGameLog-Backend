from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 비동기 엔진 생성
async_engine = create_async_engine(settings.DATABASE_URL, echo=True)
# engine = create_async_engine(
#     DATABASE_URL,
#     echo=True,
#     pool_size=5,  # 동시 연결 수
#     max_overflow=10,  # 추가로 허용할 최대 연결 수
#     pool_timeout=30,  # 연결 대기 시간
#     pool_recycle=1800,  # 연결 재사용 시간 (초)
# )

# 세션 팩토리 생성
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)
