from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ConflictException
from app.models.game import Game
from app.crud.game import get_game_in_db


async def is_existing_game(db: AsyncSession, game_name: str) -> Game:
    """
    db에 존재하는 게임인지 확인하는 함수
    Args:
        db: AsyncSession
        game_name: 찾고자 하는 게임 이름

    Returns:
        찾은 게임의 정보
    """
    game = await get_game_in_db(db, name=game_name.lower())
    if not game:
        raise NotFoundException(
            detail=f"Game [{game_name.lower()}] is not found.",
        )

    return game


async def is_not_existing_game(db: AsyncSession, game_name: str) -> None:
    """
    db에 존재하지 않는 게임인지 확인하는 함수
    Args:
        db: AsyncSession
        game_name: 확인하고자 하는 게임 이름
    """
    game = await get_game_in_db(db, name=game_name.lower())
    if game:
        raise ConflictException(f"Game [{game_name.lower()}] already exists.")
