from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# SQLAlchemy 비동기 엔진 생성
"""
- SQLAlchemy가 엔진을 사용해서 DB와 소통
- echo는 SQL 실행 로그를 출력하는 옵션. 개발 중에 켜두면 디버깅에 도움
"""
async_engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 세션 팩토리 생성
"""
- DB와의 연결을 관리하는 객체
- 세션을 통해 트랜잭션을 실행하고, ORM 모델을 사용하여 데이터베이스에 접근
- 세션을 쉽게 생성할 수 있도록 세션 팩토리 생성
- expire_on_commit=False 이면 커밋 후에도 객체가 세션에서 만료되지 않고, 계속 데이터에 접근 가능
"""
AsyncSessionLocal = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)

# redis 연결 객체
RedisClient = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DATABASE,
    decode_responses=True,  # 문자열(utf-8)로 자동 변환 / 기본값은 바이트 형태
)
