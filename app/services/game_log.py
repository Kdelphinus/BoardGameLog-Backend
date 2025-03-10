from fastapi import HTTPException

from models import Game
from domain.gamelog.gamelog_schema import GameLogCreate


async def validate_participant_num(game: Game, game_log_info: GameLogCreate) -> None:
    if (
        game_log_info.participant_num < game.min_possible_num
        or game_log_info.participant_num > game.max_possible_num
    ):
        raise HTTPException(
            status_code=422,
            detail="Participant_num must between min_possible_num and max_possible_num.",
        )
