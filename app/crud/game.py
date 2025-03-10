from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.game import Game
from app.schemas.game import GameCreate


async def create_game_in_db(db: AsyncSession, game_info: GameCreate) -> None:
    """
    db에 게임 정보를 생성하는 함수
    Args:
        db: AsyncSession
        game_info: 생성할 게임의 정보가 담긴 데이터

    Returns:
        None
    """
    db_game = Game(
        name=game_info.name,
        weight=game_info.weight,
        max_possible_num=game_info.max_possible_num,
        min_possible_num=game_info.min_possible_num,
    )
    db.add(db_game)
    await db.commit()


async def get_game_in_db(db: AsyncSession, name: str = None):
    """
    db에 있는 게임 정보를 이름으로 반환하는 함수
    Args:
        db: AsyncSession
        name: 찾고자 하는 게임 이름

    Returns:
        1) name이 있을 때: 찾는 게임의 정보
        2) name이 없을 때: 전체 게임의 정보
    """
    if name:
        result = await db.execute(select(Game).where((Game.name == name)))
        return result.scalars().first()
    results = await db.execute(select(Game))
    return results.scalars().all()
