from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import NotAcceptableException, UnprocessableEntityException
from app.models.user import User
from app.models.game import Game
from app.api.dependencies import get_db
from app.core.security import get_current_user_in_db
from app.crud.game_log import (
    create_game_log_in_db,
    get_game_log_in_db,
    update_game_log_in_db,
    delete_game_log_in_db,
)
from app.schemas.game_log import GameLogCreate, GameLogUpdate
from app.services.game import is_existing_game
from app.services.game_log import validate_participant_num, is_existing_game_log

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game_log(
    game_log_info: GameLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_in_db),
):
    """
    게임 기록 생성하는 API
    Args:
        game_log_info: 생성할 게임 기록이 담긴 데이터
        db: AsyncSession
        current_user: 현재 사용자
    """
    game = await is_existing_game(db, game_log_info.game_name)
    await validate_participant_num(game, game_log_info.participant_num)
    await create_game_log_in_db(db, game_log_info, user=current_user, game=game)


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_game_log(db: AsyncSession = Depends(get_db)):
    """
    모든 게임 기록 반환하는 API
    Args:
        db: AsyncSession

    Returns:
        전체 게임 기록
    """
    return await get_game_log_in_db(db)


@router.get("/list/my", status_code=status.HTTP_200_OK)
async def get_game_log_by_user(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_in_db),
):
    """
    현재 사용자의 게임 기록 반환하는 API
    Args:
        db: AsyncSession
        current_user: 현재 사용자

    Returns:
        현재 사용자가 생성한 기록
    """
    return await get_game_log_in_db(db, user=current_user)


@router.get("/list/my/{game_name}", status_code=status.HTTP_200_OK)
async def get_game_log_by_user_and_game(
    game_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_in_db),
):
    """
    현재 사용자의 특정 게임 기록을 반환하는 API
    Args:
        game_name: 찾고자 하는 게임 이름
        db: AsyncSession
        current_user: 현재 사용자

    Returns:
        현재 사용자의 특정 게임 기록들
    """
    game = await is_existing_game(db, game_name)
    return await get_game_log_in_db(db, user=current_user, game=game)


@router.get("/list/{game_name}", status_code=status.HTTP_200_OK)
async def get_game_log_by_game(game_name: str, db: AsyncSession = Depends(get_db)):
    """
    특정 게임의 기록을 반환하는 API
    Args:
        game_name: 찾고자 하는 게임 이름
        db: AsyncSession

    Returns:
        찾고자 하는 게임의 기록
    """
    game = await is_existing_game(db, game_name)
    return await get_game_log_in_db(db, game=game)


@router.patch("/patch/my/{game_log_id}", status_code=status.HTTP_200_OK)
async def update_game_log(
    game_log_id: int,
    game_log_update: GameLogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_in_db),
):
    """
    게임 기록을 수정하는 API
    Args:
        game_log_id: 수정하고자 하는 게임 id
        game_log_update: 변경하려는 정보
        db: AsyncSession
        current_user: 현재 사용자

    Returns:
        변경된 게임 기록
    """
    game_log = await is_existing_game_log(db, game_log_id)
    if game_log.user_id != current_user.id:
        raise NotAcceptableException(detail="You are not the owner of this game log")

    update_data = game_log_update.model_dump(exclude_unset=True)
    game: Game = game_log.game

    if "during_time" in update_data and update_data["during_time"] <= 0:
        raise NotAcceptableException(detail="During time cannot be negative")

    if "participant_num" in update_data:
        await validate_participant_num(game, update_data["participant_num"])

    if "subject" in update_data and not update_data["subject"].strip():
        raise NotAcceptableException(detail="Subject cannot be empty")

    if not update_data:
        raise NotAcceptableException()

    return await update_game_log_in_db(db, game_log, update_data)


@router.delete("/delete/my/{game_log_id}", status_code=status.HTTP_200_OK)
async def delete_game_log(
    game_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_in_db),
) -> dict[str, str]:
    """
    게임 기록을 삭제하는 함수
    Args:
        game_log_id: 삭제하고자 하는 게임 기록
        db: AsyncSession
        current_user: 현재 사용자

    Returns:
        삭제가 완료되었다는 메시지
    """
    game_log = await is_existing_game_log(db, game_log_id)
    if game_log.user_id != current_user.id:
        raise NotAcceptableException(detail="You are not the owner of this game log")
    return await delete_game_log_in_db(db, game_log)
