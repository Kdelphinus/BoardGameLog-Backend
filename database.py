import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# PostgreSQL 연결 설정
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# 비동기 엔진 생성
engine = create_async_engine(DATABASE_URL, echo=True)
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
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Base 클래스 생성 (모든 모델이 이를 상속함)
Base = declarative_base()


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
