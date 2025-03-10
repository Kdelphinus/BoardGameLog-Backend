from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.core.exceptions import NotAcceptableException
from app.crud.user import create_user_in_db, get_user_in_db
from app.schemas.user import UserCreate, Token
from app.core.security import verify_user, get_current_user_in_db
from app.services.user import is_existing_user, is_not_existing_user
from app.models.user import User

router = APIRouter()


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
async def create_user(_user_info: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    사용자를 생성하는 API
    """
    if _user_info.name.lower() == "all":
        raise NotAcceptableException(detail="Could not use this name")
    await is_not_existing_user(db, name=_user_info.name, email=_user_info.email)
    await create_user_in_db(db=db, user_info=_user_info)


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    로그인을 위한 액세스 토큰을 발급하는 API
    """
    return await verify_user(form_data, db)


@router.get("/list/me", status_code=status.HTTP_200_OK)
async def get_current_user(
    current_user: User = Depends(get_current_user_in_db),
):
    """
    현재 로그인한 사용자 정보를 반환하는 API
    """
    return current_user


@router.get("/list/{user_name}", status_code=status.HTTP_200_OK)
async def get_user(user_name: str, db: AsyncSession = Depends(get_db)):
    """
    특정 사용자 정보를 반환하는 API
    """
    user = await is_existing_user(db, name=user_name)
    return user


# TODO 개발을 위한 임시 API
@router.get("/list", status_code=status.HTTP_200_OK)
async def get_all_user(db: AsyncSession = Depends(get_db)):
    """
    사용자 전체 정보를 반환하는 API
    """
    return await get_user_in_db(db)
