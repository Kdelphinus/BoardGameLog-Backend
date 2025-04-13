from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnprocessableEntityException, NotFoundException
from app.models.game import Game
from app.models.game_log import GameLog
from app.crud.game_log import get_game_log_in_db


async def validate_participant_num(game: Game, participant_num: int) -> None:
    """
    참석 인원이 유효한지 확인하는 함수
    Args:
        game: 진행한 게임
        participant_num: 게임에 참여한 인원 수
    """
    if (
        participant_num < game.min_possible_num
        or participant_num > game.max_possible_num
    ):
        raise UnprocessableEntityException(
            detail="Participant_num must between min_possible_num and max_possible_num.",
        )


async def is_existing_game_log(db: AsyncSession, game_log_id: int) -> GameLog:
    """
    주어진 id가 존재하는 게임 기록의 id인지 확인하는 함수
    Args:
        db: AsyncSession
        game_log_id: 찾고자 하는 게임 기록의 id

    Returns:
        있을 경우, 찾고자 하는 게임의 기록
    """
    game_log = await get_game_log_in_db(db=db, game_log_id=game_log_id)
    if not game_log:
        raise NotFoundException(
            detail=f"Game log [{game_log_id}] is not found.",
        )
    return game_log
