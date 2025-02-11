from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import User
from domain.user.user_schema import UserCreate

# bcrypt 알고리즘을 사용하여 암호화하는 객체 생성
# 이후 로그인에서도 암호화하여 동일한지 확인하면 되기에 복호화는 필요없다.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_user(db: AsyncSession, user_create: UserCreate):
    db_user = User(
        name=user_create.name,
        password=pwd_context.hash(user_create.password),
        email=user_create.email,
    )
    db.add(db_user)
    await db.commit()


# 생성하고자 하는 회원 정보가 이미 있는지 확인하는 함수
async def get_existing_user(db: AsyncSession, user_create: UserCreate):
    result = await db.execute(
        select(User).where(
            (User.name == user_create.name) | (User.email == user_create.email)
        )
    )
    return result.scalars().first()


async def get_user(db: AsyncSession, name: str):
    result = await db.execute(select(User).where(User.name == name))
    return result.scalars().first()
