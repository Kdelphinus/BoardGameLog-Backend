from app.core.exceptions import UnprocessableEntityException
from app.models.game import Game
from app.schemas.game_log import GameLogCreate


async def validate_participant_num(game: Game, game_log_info: GameLogCreate) -> None:
    if (
        game_log_info.participant_num < game.min_possible_num
        or game_log_info.participant_num > game.max_possible_num
    ):
        raise UnprocessableEntityException(
            detail="Participant_num must between min_possible_num and max_possible_num.",
        )
