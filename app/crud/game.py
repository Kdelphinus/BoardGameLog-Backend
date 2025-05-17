from typing import Any

from sqlalchemy import Sequence
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
        cover_image=game_info.cover_image,
    )
    db.add(db_game)
    await db.commit()


async def get_game_in_db(db: AsyncSession, name: str = None) -> Game | Sequence[Game]:
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


async def update_game_in_db(
    db: AsyncSession, game: Game, update_data: dict[str, Any]
) -> Game:
    """
    db에 있는 게임의 정보를 수정하는 함수
    Args:
        db: AsyncSession
        game: 변경할 게임
        update_data: 변경할 내용이 담긴 딕셔너리

    Returns:
        주어진 정보로 데이터를 수정한 게임
    """
    for key, value in update_data.items():
        setattr(game, key, value)

    await db.commit()
    await db.refresh(game)  # 방금 커밋된 최신 데이터를 다시 game 객체에 반영(동기화)
    return game


async def delete_game_in_db(db: AsyncSession, game: Game) -> dict[str, str]:
    """
    db에 있는 게임을 삭제하는 함수
    Args:
        db: AsyncSession
        game: 삭제하고자 하는 게임

    Returns:
        삭제가 완료되었다는 메시지
    """
    await db.delete(game)
    await db.commit()

    return {"message": f"{game.name} deleted"}
