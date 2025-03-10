from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models import Game
from domain.game.game_crud import get_game


async def is_exist_game(db: AsyncSession, game_name: str) -> Game:
    game = await get_game(db, name=game_name.lower())
    if not game:
        raise HTTPException(
            status_code=404,
            detail=f"Game [{game_name.lower()}] is not found.",
        )

    return game


async def is_not_exist_game(db: AsyncSession, game_name: str) -> None:
    game = await get_game(db, name=game_name.lower())
    if game:
        raise HTTPException(
            status_code=409, detail=f"{game_name.lower()} is already exists."
        )
