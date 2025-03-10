from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models import User, Game, GameLog
from domain.gamelog.gamelog_schema import GameLogCreate


async def create_game_log(
    db: AsyncSession, game_log_info: GameLogCreate, user: User, game: Game
) -> None:
    db_game_log = GameLog(
        user_id=user.id,
        game_id=game.id,
        date=datetime.now(),
        during_time=game_log_info.during_time,
        participant_num=game_log_info.participant_num,
        content=game_log_info.content,
        picture=game_log_info.picture,
    )
    db.add(db_game_log)
    await db.commit()


async def get_game_log(db: AsyncSession, user: User = None, game: Game = None):
    if not user and not game:
        results = await db.execute(select(GameLog))
    elif user and game:
        results = await db.execute(
            select(GameLog).where(
                (GameLog.user_id == user.id) and (GameLog.game_id == game.id)
            )
        )
    elif user:
        results = await db.execute(select(GameLog).where(GameLog.user_id == user.id))
    else:
        results = await db.execute(select(GameLog).where(GameLog.game_id == game.id))

    return results.scalars().all()
