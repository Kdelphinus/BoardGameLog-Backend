from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.api.dependencies import get_db
from app.schemas.game import GameCreate
from app.crud.game import create_game_in_db, get_game_in_db
from app.services.game import is_not_existing_game, is_existing_game

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game(game_info: GameCreate, db: AsyncSession = Depends(get_db)):
    """
    게임 정보를 생성하는 API
    Args:
        game_info: 생성할 게임의 정보
        db: AsyncSession
    """
    await is_not_existing_game(db, game_name=game_info.name)
    await create_game_in_db(db, game_info)


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_game(db: AsyncSession = Depends(get_db)):
    """
    등록된 모든 게임 목록을 반환하는 API
    Args:
        db: AsyncSession

    Returns:
        전체 게임 목록
    """
    return await get_game_in_db(db)


@router.get("/list/{game_name}", status_code=status.HTTP_200_OK)
async def get_game(game_name: str, db: AsyncSession = Depends(get_db)):
    """
    주어진 게임의 정보를 반환하는 API
    Args:
        game_name: 불러올 게임의 이름
        db: AsyncSession

    Returns:
        요청한 게임의 정보
    """
    game = await is_existing_game(db, game_name)
    return game
