from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import Game
from domain.game.game_schema import GameCreate


async def create_game(db: AsyncSession, game_info: GameCreate) -> None:
    db_game = Game(
        name=game_info.name,
        weight=game_info.weight,
        max_possible_num=game_info.max_possible_num,
        min_possible_num=game_info.min_possible_num,
    )
    db.add(db_game)
    await db.commit()


async def get_game(db: AsyncSession, name: str):
    result = await db.execute(select(Game).where((Game.name == name)))
    return result.scalars().first()


async def get_all_game(db: AsyncSession):
    results = await db.execute(select(Game))
    return results.scalars().all()
