from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.game_log_like import check_game_log_likes_in_db
from app.models.game_log_like import GameLogLike


async def is_existing_game_log_like(
    db: AsyncSession, game_log_id: int, user_name: str
) -> GameLogLike | None:
    """
    주어진 id에 사용자의 좋아요가 존재하는지 확인하는 함수
    Args:
        db: AsyncSession
        game_log_id: 찾고자 하는 게임 기록의 id
        user_name: 찾고자 하는 사용자의 이름

    Returns:
        GameLogLike 혹은 None
    """
    existing_like = await check_game_log_likes_in_db(db, game_log_id, user_name)
    return existing_like
