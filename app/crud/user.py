from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import pwd_context


async def create_user_in_db(db: AsyncSession, user_info: UserCreate):
    """
    db에 사용자를 생성하는 함수
    Args:
        db: AsyncSession
        user_info: 생성할 사용자의 정보

    Returns:
        None
    """

    db_user = User(
        name=user_info.name,
        password=pwd_context.hash(user_info.password),
        email=user_info.email,
    )
    db.add(db_user)
    await db.commit()


async def get_user_in_db(db: AsyncSession, name: str = None, email: EmailStr = None):
    """
    db에 있는 사용자 정보를 가져오는 함수
    Args:
        db: AsyncSession
        name: 가져올 사용자의 이름
        email: 가져올 사용자의 이메일

    Returns:
        1) name 값이 있을 때: 특정 사용자 정보 반환
        2) email 값이 있을 때: 특정 사용자 정보 반환
        3) name, email 값이 모두 없을 때: 모든 사용자 정보 반환
    """
    if not name and not email:
        results = await db.execute(select(User))
        return results.scalars().all()
    elif name and email:
        result = await db.execute(
            select(User).where((User.name == name) | (User.email == email))
        )
    elif name:
        result = await db.execute(select(User).where(User.name == name))

    else:
        result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()
