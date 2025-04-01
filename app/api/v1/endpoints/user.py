from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis
from typing import List

from app.api.dependencies import get_db, get_redis
from app.config import settings
from app.core.exceptions import (
    NotAcceptableException,
    CredentialsException,
    UnprocessableEntityException,
)
from app.crud.user import (
    create_user_in_db,
    get_user_in_db,
    update_user_in_db,
    soft_delete_user_in_db,
    hard_delete_user_in_db,
)
from app.schemas.user import (
    UserResponse,
    UserCreate,
    AccessToken,
    UserUpdate,
    RefreshToken,
    PasswordResetRequest,
    PasswordResetConfirm,
    RestoreUserRequest,
    RestoreUserConfirm,
)
from app.core.security import (
    issue_access_token,
    reissue_access_token,
    delete_token,
    get_current_user_in_db,
    send_reset_password_email,
    reset_password,
    send_restore_email,
    restore_user,
)
from app.services.user import is_existing_user, is_not_existing_user
from app.models.user import User

router = APIRouter()


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_user(_user_info: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    사용자를 생성하는 API
    Args:
        _user_info: 생성할 사용자의 정보
        db: AsyncSession
    """
    if _user_info.name.lower() == "all":
        raise NotAcceptableException(detail="Could not use this name")
    await is_not_existing_user(db=db, name=_user_info.name, email=_user_info.email)
    await create_user_in_db(db=db, user_info=_user_info)


@router.post("/login", response_model=AccessToken)
async def login(
    db: AsyncSession = Depends(get_db),
    redis_db: Redis = Depends(get_redis),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    로그인을 위한 액세스 토큰을 발급하는 API
    Args:
        db: AsyncSession
        redis_db: redis db
        form_data: 요청 하는 자료

    Returns:
        액세스 토큰
    """
    return await issue_access_token(db=db, redis_db=redis_db, form_data=form_data)


@router.post("/refresh", response_model=RefreshToken)
async def refresh(request: Request, redis_db: Redis = Depends(get_redis)):
    """
    리프레시 토큰을 이용해 새로운 액세스 토큰을 발급하는 API
    Args:
        request: Request
        redis_db: redis db

    Returns:
        새로운 액세스 토큰
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise CredentialsException(detail="Invalid authorization header")

    refresh_token = authorization.split(" ")[1]
    return await reissue_access_token(refresh_token=refresh_token, redis_db=redis_db)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, redis_db: Redis = Depends(get_redis)):
    """
    액세스 토큰을 블랙리스트에 올리고, 리프레시 토큰을 삭제하는 API
    Args:
        request: Request
        redis_db: redis db
    """
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise CredentialsException(detail="Invalid authorization header")

    access_token = authorization.split(" ")[1]
    return await delete_token(redis_db=redis_db, token=access_token)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def request_reset_password(
    data: PasswordResetRequest, db: AsyncSession = Depends(get_db)
):
    """
    비밀번호 재설정을 요청하는 API
    Args:
        data: 변경하고자 하는 사용자의 이름이 담긴 데이터
        db: AsyncSession

    Returns:
        최종 -> 이메일 발송 여부
        현재 -> reset token
    """
    user: User = await is_existing_user(db=db, name=data.name)
    return await send_reset_password_email(name=user.name, email=user.email)


@router.post("/reset-password/confirm", status_code=status.HTTP_200_OK)
async def confirm_reset_password(
    data: PasswordResetConfirm, db: AsyncSession = Depends(get_db)
):
    """
    비밀번호 재설정을 승인하는 API
    Args:
        data: 변경 권한을 가진 토큰과 새로운 비밀번호가 담긴 데이터
        db: AsyncSession

    Returns:
        변경 완료 메시지
    """
    return reset_password(token=data.token, new_password=data.new_password, db=db)


@router.get("/list/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_user_in_db),
):
    """
    현재 로그인한 사용자 정보를 반환하는 API
    Args:
        current_user: 현재 사용자 정보

    Returns:
        현재 사용자의 정보
    """
    return current_user


@router.get(
    "/list/deactivate",
    status_code=status.HTTP_200_OK,
    response_model=List[UserResponse],
)
async def get_all_deactivate_user(db: AsyncSession = Depends(get_db)):
    """
    모든 비활성화된 사용자 정보를 반환 하는 API
    Args:
        db: AsyncSession

    Returns:
        db에 있는 모든 비활성화된 사용자의 정보
    """
    return await get_user_in_db(db, is_deleted=True)


@router.get(
    "/list/{user_name}", status_code=status.HTTP_200_OK, response_model=UserResponse
)
async def get_user(user_name: str, db: AsyncSession = Depends(get_db)):
    """
    특정 사용자 정보를 반환 하는 API
    Args:
        user_name: 사용자의 이름
        db: AsyncSession

    Returns:
        찾고자 하는 사용자의 정보
    """
    user = await is_existing_user(db, name=user_name)
    return user


@router.get("/list", status_code=status.HTTP_200_OK, response_model=List[UserResponse])
async def get_all_user(db: AsyncSession = Depends(get_db)):
    """
    사용자 전체 정보를 반환 하는 API
    Args:
        db: AsyncSession

    Returns:
        db에 있는 모든 사용자의 정보
    """
    return await get_user_in_db(db)


@router.patch("/patch", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    사용자 정보를 수정하는 API
    Args:
        user_update: 갱신할 사용자의 정보
        current_user: 현재 사용자
        db: AsyncSession

    Returns:
        갱신된 사용자의 정보
    """
    # 업데이트할 데이터 필터링 (None이 아닌 값만 업데이트)
    update_data = user_update.model_dump(exclude_unset=True)

    # 이메일 또는 사용자 이름 업데이트 시 중복 확인
    if "email" in update_data and update_data["email"] is not None:
        await is_not_existing_user(db, email=update_data["email"])

    return await update_user_in_db(db, user=current_user, update_data=update_data)


@router.patch("/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def soft_delete_user(
    request: Request,
    redis_db: Redis = Depends(get_redis),
    current_user: User = Depends(get_current_user_in_db),
    db: AsyncSession = Depends(get_db),
):
    """
    사용자를 soft delete 시키는 API
    Args:
        request: Request
        redis_db: redis db
        current_user: 현재 사용자
        db: AsyncSession
    """
    await soft_delete_user_in_db(db, current_user)
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise CredentialsException(detail="Invalid authorization header")

    access_token = authorization.split(" ")[1]
    await delete_token(redis_db=redis_db, token=access_token)


@router.post("/restore", status_code=status.HTTP_200_OK)
async def request_restore_user(
    data: RestoreUserRequest, db: AsyncSession = Depends(get_db)
):
    """
    soft delete 되었던 사용자를 복구 요청하는 API
    Args:
        data: 복구할 사용자의 정보가 담긴 데이터
        db: AsyncSession

    Returns:
        이메일이 발송되었다는 메일
    """
    user: User = await is_existing_user(db=db, name=data.name, is_deleted=True)
    return await send_restore_email(name=user.name, email=user.email)


@router.post("/restore/confirm", status_code=status.HTTP_200_OK)
async def confirm_restore_user(
    data: RestoreUserConfirm, db: AsyncSession = Depends(get_db)
):
    """
    soft delete 되었던 사용자의 복구를 승인하는 API
    Args:
        data: 복구할 사용자의 정보가 담긴 데이터
        db: AsyncSession

    Returns:
        복구가 완료되었다는 메일 발송 메시지
    """
    return await restore_user(token=data.token, db=db)


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_user(db: AsyncSession = Depends(get_db)):
    """
    hard delete 하는 API
    Args:
        db: AsyncSession

    Returns:

    """
    return await hard_delete_user_in_db(
        db=db, delete_threshold_day=settings.HARD_DELETE_USER_DAYS
    )
