from typing import Any

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


async def get_user_in_db(
    db: AsyncSession, name: str = None, email: EmailStr = None, is_deleted: bool = False
):
    """
    db에 있는 사용자 정보를 가져오는 함수
    Args:
        db: AsyncSession
        name: 가져올 사용자의 이름
        email: 가져올 사용자의 이메일
        is_deleted: 삭제된 사용자를 가져올 것인지 유무

    Returns:
        1) name 값이 있을 때: 특정 사용자 정보 반환
        2) email 값이 있을 때: 특정 사용자 정보 반환
        3) name, email 값이 모두 없을 때: 모든 사용자 정보 반환
    """
    if not name and not email:
        results = await db.execute(select(User).where(User.is_deleted == is_deleted))
        return results.scalars().all()
    elif name and email:
        result = await db.execute(
            select(User).where(
                ((User.name == name) | (User.email == email))
                & (User.is_deleted == is_deleted)
            )
        )
    elif name:
        result = await db.execute(
            select(User).where((User.name == name) & (User.is_deleted == is_deleted))
        )

    else:
        result = await db.execute(
            select(User).where((User.email == email) & (User.is_deleted == is_deleted))
        )
    return result.scalars().first()


async def update_user_in_db(
    db: AsyncSession, user: User, update_data: dict[str, Any]
) -> User:
    """
    db에 있는 사용자의 정보를 수정하는 함수
    Args:
        db: AsyncSession
        user: 변경할 사용자
        update_data: 변경할 내용이 담긴 딕셔너리

    Returns:
        주어진 정보로 데이터를 수정한 사용자
    """
    for key, value in update_data.items():
        setattr(user, key, value)

    await db.commit()
    await db.refresh(user)
    return user


async def soft_delete_user_in_db(db: AsyncSession, user: User) -> None:
    """
    soft delete를 수행하는 함수
    Args:
        db: AsyncSession
        user: 삭제할 사용자
    """
    user.is_deleted = True
    user.deleted_at = datetime.now()
    await db.commit()
    await db.refresh(user)


async def hard_delete_user_in_db(
    db: AsyncSession, delete_threshold_day: int
) -> dict[str, str]:
    """
    hard delete 하는 함수
    Args:
        db: AsyncSession
        delete_threshold_day: 영구 삭제하는 임계점

    Returns:
        결과 메시지
    """
    delete_threshold = datetime.now() - timedelta(days=delete_threshold_day)

    results = await db.execute(
        select(User).where(User.is_deleted == True, User.deleted_at <= delete_threshold)
    )
    users_to_delete = results.scalars().all()

    if not users_to_delete:
        return {"message": "No users to delete"}

    for user in users_to_delete:
        await db.delete(user)

    await db.commit()

    return {"message": f"Deleted {len(users_to_delete)} users."}
