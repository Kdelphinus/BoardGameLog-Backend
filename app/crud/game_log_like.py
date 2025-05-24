from typing import Sequence

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.game_log_like import GameLogLike


async def create_game_log_like_in_db(
    db: AsyncSession, game_log_id: int, user_name: str
) -> None:
    """
    좋아요를 생성하는 함수
    Args:
        db: AsyncSession
        game_log_id: 연관된 게임 기록
        user_name: 좋아요를 누른 사용자
    """
    db_like = GameLogLike(user_name=user_name, game_log_id=game_log_id, flag=True)
    db.add(db_like)
    await db.commit()


async def check_game_log_likes_in_db(
    db: AsyncSession,
    game_log_id: int,
    user_name: str,
) -> GameLogLike | None:
    """
    좋아요가 있는지 확인하는 함수
    Args:
        db: AsyncSession
        game_log_id: 연관된 게임 기록
        user_name: 사용자 이름

    Returns:

    """
    result = await db.execute(
        select(GameLogLike).where(
            and_(
                GameLogLike.game_log_id == game_log_id,
                GameLogLike.user_name == user_name,
            )
        )
    )
    return result.scalars().first()


async def get_game_log_likes_in_db(
    db: AsyncSession,
    game_log_id: int,
    flag: bool = True,
    skip: int = 0,
    limit: int = 100,
) -> Sequence[GameLogLike]:
    """
    활성화 된 좋아요의 리스트를 반환하는 함수
    Args:
        db: AsyncSession
        game_log_id: 연관된 게임 기록
        flag: 활성화 유무
        skip: 어디서부터 불러올 지
        limit: 어디까지 불러올 지

    Returns:
        활성화된 좋아요의 리스트
    """
    if skip is None or limit is None:
        result = await db.execute(
            select(GameLogLike).where(
                and_(GameLogLike.game_log_id == game_log_id, GameLogLike.flag == flag)
            )
        )
        return result.scalars().all()

    result = await db.execute(
        select(GameLogLike)
        .where(and_(GameLogLike.game_log_id == game_log_id, GameLogLike.flag == flag))
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_game_log_like_in_db(
    db: AsyncSession, game_log_like: GameLogLike
) -> GameLogLike:
    """
    좋아요의 상태를 변경하는 함수
    Args:
        db: AsyncSession
        game_log_like: 상태를 변경할 좋아요

    Returns:
        변경된 좋아요
    """
    setattr(game_log_like, "flag", not game_log_like.flag)

    await db.commit()
    await db.refresh(game_log_like)
    return game_log_like


async def delete_game_log_like_in_db(db: AsyncSession) -> None:
    """
    비활성화된 좋아요를 삭제하는 함수
    Args:
        db: AsyncSession
    """
    results = await db.execute(select(GameLogLike).where(GameLogLike.flag == False))
    dislike_to_delete = results.scalars().all()
    if dislike_to_delete:
        for dislike in dislike_to_delete:
            await db.delete(dislike)
        await db.commit()
