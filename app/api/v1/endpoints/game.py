from fastapi import APIRouter, Depends
from sqlalchemy import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from typing import List

from app.models.game import Game
from app.api.dependencies import get_db
from app.core.exceptions import UnprocessableEntityException
from app.schemas.game import GameCreate, GameUpdate, GameResponse
from app.crud.game import (
    create_game_in_db,
    get_game_in_db,
    update_game_in_db,
    delete_game_in_db,
)
from app.services.game import is_not_existing_game, is_existing_game

from app.models.user import User
from app.core.security import get_admin_user_in_db

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_game(
    game_info: GameCreate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user_in_db),
) -> None:
    """
    게임 정보를 생성하는 API
    Args:
        game_info: 생성할 게임의 정보
        db: AsyncSession
        admin_user: 현재 관리자
    """
    await is_not_existing_game(db, game_name=game_info.name)
    await create_game_in_db(db, game_info)


@router.get("/list", status_code=status.HTTP_200_OK, response_model=List[GameResponse])
async def get_all_game(db: AsyncSession = Depends(get_db)) -> Sequence[Game]:
    """
    등록된 모든 게임 목록을 반환하는 API
    Args:
        db: AsyncSession

    Returns:
        전체 게임 목록
    """
    return await get_game_in_db(db)


@router.get(
    "/list/{game_name}", status_code=status.HTTP_200_OK, response_model=GameResponse
)
async def get_game(game_name: str, db: AsyncSession = Depends(get_db)) -> Game:
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


@router.patch(
    "/patch/{game_name}", status_code=status.HTTP_200_OK, response_model=GameResponse
)
async def update_game(
    game_name: str,
    game_update: GameUpdate,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user_in_db),
) -> Game:
    """
    주어진 게임의 정보를 수정하는 API
    Args:
        game_name: 수정하려는 게임의 이름
        game_update: 변경하려는 정보
        db: AsyncSession
        admin_user: 현재 관리자

    Returns:
        변경한 게임 객체
    """
    update_data = game_update.model_dump(exclude_unset=True)
    game = await is_existing_game(db=db, game_name=game_name)

    if "name" in update_data and update_data["name"].strip() is not None:
        await is_not_existing_game(db, game_name=update_data["name"].lower())
        update_data["name"] = update_data["name"].lower()

    if "weight" in update_data and not (0 <= update_data["weight"] <= 5):
        raise UnprocessableEntityException(detail="Weight value must between 0 and 5.")

    if "min_possible_num" in update_data and "max_possible_num" in update_data:
        if (
            update_data["min_possible_num"] <= 0
            or update_data["min_possible_num"] > update_data["max_possible_num"]
        ):
            raise UnprocessableEntityException(detail="인원은 0명보다 많아야 합니다.")
    elif "min_possible_num" in update_data:
        if (
            update_data["min_possible_num"] <= 0
            or update_data["min_possible_num"] > game.max_possible_num
        ):
            raise UnprocessableEntityException(
                detail="최소 인원은 최대 인원보다 작아야 합니다."
            )
    elif "max_possible_num" in update_data:
        if update_data["max_possible_num"] < game.min_possible_num:
            raise UnprocessableEntityException(
                detail="최대 인원은 최소 인원보다 커야 합니다."
            )

    if not update_data:  # 변경할 내용이 없을 때
        raise UnprocessableEntityException()

    return await update_game_in_db(db=db, game=game, update_data=update_data)


@router.delete("/delete/{game_name}", status_code=status.HTTP_200_OK)
async def delete_game(
    game_name: str,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(get_admin_user_in_db),
) -> dict[str, str]:
    """
    주어진 게임을 삭제하는 API
    Args:
        game_name: 삭제하고자 하는 게임의 이름
        db: AsyncSession
        admin_user: 현재 관리자

    Returns:
        게임이 삭제되었다는 메시지
    """
    game = await is_existing_game(db=db, game_name=game_name)
    return await delete_game_in_db(db=db, game=game)
