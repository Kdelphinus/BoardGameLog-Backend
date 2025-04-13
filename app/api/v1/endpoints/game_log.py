from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import NotAcceptableException
from app.models.user import User
from app.api.dependencies import get_db
from app.core.security import get_current_user_in_db
from app.crud.game_log import create_game_log_in_db, get_game_log_in_db
from app.schemas.game_log import GameLogCreate
from app.services.game import is_existing_game
from app.services.game_log import validate_participant_num

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
    if game_log_info.game_name.lower() == "all":
        raise NotAcceptableException(detail="Could not using this name")
    game = await is_existing_game(db, game_log_info.game_name)
    await validate_participant_num(game, game_log_info)
    await create_game_log_in_db(db, game_log_info, user=current_user, game=game)


@router.get("/list/all", status_code=status.HTTP_200_OK)
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
