from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.game import Game
from app.models.game_log import GameLog
from app.models.user import User
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
    """
    db_game_log = GameLog(
        user_name=user.name,
        game_name=game.name,
        date=datetime.now(),
        during_time=game_log_info.during_time,
        participant_num=game_log_info.participant_num,
        subject=game_log_info.subject,
        content=game_log_info.content,
        picture=game_log_info.picture,
    )
    db.add(db_game_log)
    await db.commit()


async def get_game_log_in_db(
    db: AsyncSession, user: User = None, game: Game = None, game_log_id: int = None
):
    """
    db에 있는 게임 기록을 반환하는 함수
    Args:
        db: AsyncSession
        user: 불러올 기록을 작성한 사용자
        game: 불러올 기록에 포함된 게임
        game_log_id: 불러올 기록의 id

    Returns:
        1) user, game 입력 안 했을 때: 전체 게임 기록
        2) user, game 모두 입력 했을 때: 특정 사용자가 특정 게임을 작성한 기록
        3) user만 입력 했을 때: 특정 사용자가 기록한 게임 기록
        4) game만 입력 했을 때: 특정 게임이 작성된 기록
        5) game_log_id 입력 시: 특정 기록
    """
    if game_log_id:
        result = await db.execute(select(GameLog).where(GameLog.id == game_log_id))
        return result.scalars().first()

    if not user and not game:
        results = await db.execute(select(GameLog))
    elif user and game:
        results = await db.execute(
            select(GameLog).where(
                (GameLog.user_name == user.name) & (GameLog.game_name == game.name)
            )
        )
    elif user:
        results = await db.execute(
            select(GameLog).where(GameLog.user_name == user.name)
        )
    else:
        results = await db.execute(
            select(GameLog).where(GameLog.game_name == game.name)
        )

    return results.scalars().all()


async def update_game_log_in_db(
    db: AsyncSession, game_log: GameLog, update_data: dict[str, Any]
) -> GameLog:
    """
    db에 있는 게임 기록 정보를 수정하는 함수
    Args:
        db: AsyncSession
        game_log: 변경할 게임 기록
        update_data: 변경할 내용이 담긴 딕셔너리

    Returns:
        주어진 정보로 수정한 게임 기록
    """
    for key, value in update_data.items():
        setattr(game_log, key, value)

    setattr(game_log, "date", datetime.now())

    await db.commit()
    await db.refresh(game_log)
    return game_log


async def delete_game_log_in_db(db: AsyncSession, game_log: GameLog) -> dict[str, str]:
    """
    db에 있는 게임 기록을 삭제하는 함수
    Args:
        db: AsyncSession
        game_log: 삭제하고자 하는 게임 기록

    Returns:
        삭제가 완료되었다는 메시지
    """
    await db.delete(game_log)
    await db.commit()

    return {"message": f"{game_log.id} deleted"}
