import os

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from dotenv import load_dotenv

from models import User
from database import get_db
from domain.user.user_router import get_current_user
from domain.game.game_service import is_exist_game
from domain.gamelog.gamelog_schema import GameLogCreate
from domain.gamelog import gamelog_crud, gamelog_service

load_dotenv()

router = APIRouter(prefix=f"/api/{os.getenv("API_VERSION")}/game_log")


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game_log(
    game_log_info: GameLogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    print(game_log_info)  # TODO create 기능 정상 동작하면 지우기
    game = await is_exist_game(db, game_log_info.game_name)
    await gamelog_service.validate_participant_num(game, game_log_info)
    await gamelog_crud.create_game_log(db, game_log_info, user=current_user, game=game)


@router.get("/list/all", status_code=status.HTTP_200_OK)
async def get_all_game_log(db: AsyncSession = Depends(get_db)):
    return await gamelog_crud.get_game_log(db)


@router.get("/list/my", status_code=status.HTTP_200_OK)
async def get_game_log_by_user(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return await gamelog_crud.get_game_log(db, user=current_user)


@router.get("/list/{game_name}", status_code=status.HTTP_200_OK)
async def get_game_log_by_game(game_name: str, db: AsyncSession = Depends(get_db)):
    game = await is_exist_game(db, game_name)
    return await gamelog_crud.get_game_log(db, game=game)


@router.get("/list/my/{game_name}", status_code=status.HTTP_200_OK)
async def get_game_log_by_user_and_game(
    game_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    game = await is_exist_game(db, game_name)
    return await gamelog_crud.get_game_log(db, user=current_user, game=game)
