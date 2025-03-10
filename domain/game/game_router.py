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
    game = await game_service.is_exist_game(db, game_name)
    return game
