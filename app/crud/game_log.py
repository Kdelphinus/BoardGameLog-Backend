from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.models.game import Game
from app.models.game_log import GameLog
from app.schemas.game_log import GameLogCreate


async def create_game_log_in_db(
    db: AsyncSession, game_log_info: GameLogCreate, user: User, game: Game
) -> None:
    """
    db에 게임 기록을 생성하는 함수
    Args:
        db: AsyncSession
        game_log_info: 게임 기록에 관한 정보
        user: 게임을 기록하는 사용자
        game: 기록할 게임

    Returns:
        None
    """
    db_game_log = GameLog(
        user_id=user.id,
        game_id=game.id,
        date=datetime.now(),
        during_time=game_log_info.during_time,
        participant_num=game_log_info.participant_num,
        subject=game_log_info.subject,
        content=game_log_info.content,
        picture=game_log_info.picture,
    )
    db.add(db_game_log)
    await db.commit()


async def get_game_log_in_db(db: AsyncSession, user: User = None, game: Game = None):
    """
    db에 있는 게임 기록을 반환하는 함수
    Args:
        db: AsyncSession
        user: 불러올 기록을 작성한 사용자
        game: 불러올 기록에 포함된 게임

    Returns:
        1) user, game 입력 안 했을 때: 전체 게임 기록
        2) user, game 모두 입력 했을 때: 특정 사용자가 특정 게임을 작성한 기록
        3) user만 입력 했을 때: 특정 사용자가 기록한 게임 기록
        4) game만 입력 했을 때: 특정 게임이 작성된 기록
    """
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
