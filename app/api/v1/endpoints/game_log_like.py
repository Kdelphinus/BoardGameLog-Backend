from typing import List

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.config import settings
from app.core.security import get_current_user_in_db, get_admin_user_in_db
from app.crud.game_log_like import (
    get_game_log_likes_in_db,
    create_game_log_like_in_db,
    update_game_log_like_in_db,
    delete_game_log_like_in_db,
)
from app.models.user import User
from app.schemas.game_log_like import GameLogLike
from app.services.game_log import is_existing_game_log
from app.services.game_log_like import is_existing_game_log_like

router = APIRouter()


@router.post("/create/{game_log_id}", status_code=status.HTTP_201_CREATED)
async def create_game_log_like(
    game_log_id: int,
    current_user: User = Depends(get_current_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    좋아요를 생성하는 API
    Args:
        game_log_id: 좋아요를 누른 게임 로그
        current_user: 좋아요를 누른 사용자
        db: AsyncSession

    Returns:
        좋아요가 잘 생성되었다는 메시지
    """
    game_log = await is_existing_game_log(db, game_log_id)
    like = await is_existing_game_log_like(db, game_log_id, current_user.name)
    if like:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Like operation requested",
                "action": "PATCH",
                "game_log_id": game_log_id,
                "endpoint": f"/api/{settings.API_VERSION}/game_log_like/update/{game_log_id}",
            },
        )
    await create_game_log_like_in_db(db, game_log_id, user_name=current_user.name)
    await game_log.update_like_num(db)
    return {"message": "Successfully liked the game log"}


@router.get("/is_liked/{game_log_id}")
async def check_game_log_like(
    game_log_id: int,
    current_user: User = Depends(get_current_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    좋아요가 있는지 확인하는 API
    Args:
        game_log_id: 확인하고자 하는 게임 기록
        current_user: 현재 사용자
        db: AsyncSession

    Returns:
        좋아요를 눌렀는지 안 눌렀는지 확인
    """
    like = await is_existing_game_log_like(db, game_log_id, user_name=current_user.name)
    if not like:
        return {"is_liked": False}
    return {"is_liked": like.flag}


@router.get("/list/{game_log_id}", response_model=List[GameLogLike])
async def get_game_log_like_list(
    game_log_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """
    게임 기록에 눌린 좋아요 리스트를 가져오는 API
    Args:
        game_log_id: 게임 기록
        skip: 어디서부터 가져올 것인지
        limit: 얼마나 가져올 것인지
        db: AsyncSession

    Returns:
        좋아요 리스트
    """
    likes = await get_game_log_likes_in_db(db, game_log_id, skip=skip, limit=limit)
    return likes


@router.patch("/update/{game_log_id}", status_code=status.HTTP_200_OK)
async def update_game_log_like(
    game_log_id: int,
    current_user: User = Depends(get_current_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    좋아요를 수정하는 API
    Args:
        game_log_id: 수정하고자 하는 좋아요와 연관된 게임 기록
        current_user: 현재 사용자
        db: AsyncSession

    Returns:
        좋아요가 눌려 있으면 해제, 안 눌려 있으면 활성
    """
    game_log = await is_existing_game_log(db, game_log_id)
    like = await is_existing_game_log_like(db, game_log_id, current_user.name)
    if not like:  # 307은 POST 요청 내용을 유지
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Like operation requested",
                "action": "POST",
                "game_log_id": game_log_id,
                "endpoint": f"/api/{settings.API_VERSION}/game_log_like/create/{game_log_id}",
            },
        )
    updated_game_log_like = await update_game_log_like_in_db(db, game_log_like=like)
    await game_log.update_like_num(db)
    return updated_game_log_like


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_log_like(
    admin_user: User = Depends(get_admin_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    해제되어 있는 좋아요를 삭제하는 API
    Args:
        admin_user: 관리자 계정 인증
        db: AsyncSession
    """
    await delete_game_log_like_in_db(db)
