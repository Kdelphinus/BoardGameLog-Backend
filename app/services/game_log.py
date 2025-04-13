from app.core.exceptions import UnprocessableEntityException
from app.models.game import Game
from app.schemas.game_log import GameLogCreate


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
