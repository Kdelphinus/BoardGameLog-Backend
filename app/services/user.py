from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.crud.user import get_user_in_db


async def is_existing_user(
    db: AsyncSession, name: str, email: str = None, is_deleted: bool = False
):
    """
    db에 이미 존재하는 사용자인지 확인하는 함수
    Args:
        db: AsyncSession
        name: 확인할 사용자의 이름
        email: 확인할 사용자의 이메일
        is_deleted: 삭제된 사용자를 확인할 지 확인

    Returns:
        찾고자 하는 사용자
    """
    user = await get_user_in_db(db, name=name, email=email, is_deleted=is_deleted)
    if not user:
        raise NotFoundException(f"User [{name}] is not found.")
    return user


async def is_not_existing_user(
    db: AsyncSession, name: str = None, email: str = None
) -> None:
    """
    db에 없는 사용자인지 확인하는 함수
    Args:
        db: AsyncSession
        name: 확인할 사용자의 이름
        email: 확인할 사용자의 이메일

    Returns:

    """
    user = await get_user_in_db(db, name=name, email=email)
    if user:
        raise ConflictException(f"User [{name}] already exists.")
