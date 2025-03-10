import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from dotenv import load_dotenv

from database import get_db
from domain.game import game_crud, game_schema, game_service

load_dotenv()

router = APIRouter(prefix=f"/api/{os.getenv("API_VERSION")}/game")


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game(
    game_info: game_schema.GameCreate, db: AsyncSession = Depends(get_db)
):
    await game_service.is_not_exist_game(db, game_name=game_info.name)
    await game_crud.create_game(db, game_info)


@router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_game(db: AsyncSession = Depends(get_db)):
    return await game_crud.get_all_game(db)


@router.get("/list/{game_name}", status_code=status.HTTP_200_OK)
async def get_game(game_name: str, db: AsyncSession = Depends(get_db)):
    game = await game_crud.get_game(db, name=game_name.lower())
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="게임이 존재하지 않습니다."
        )
    return game


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game(
    _game_info: game_schema.GameCreate, db: AsyncSession = Depends(get_db)
):
    game = await game_crud.get_game(db, name=_game_info.name)
    if game:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 게임입니다."
        )
    await game_crud.create_game(db=db, game_info=_game_info)
