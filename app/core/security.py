import jwt

from datetime import datetime, timezone, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import CredentialsException
from app.api.dependencies import get_db

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{settings.API_VERSION}/users/login"
)

# bcrypt 알고리즘을 사용하여 암호화하는 객체
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def verify_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """
    해당 사용자가 인증된 사용자인지 확인하는 함수
    Args:
        form_data: 현재 요청받은 데이터
        db: AsyncSession

    Returns:
        액세스 토큰 발급
    """
    from app.crud.user import get_user_in_db  # 순환 참조를 막기 위한 지연 참조

    user = await get_user_in_db(db, form_data.username)
    # 암호화되지 않은 비밀번호를 암호화하여 데이터베이스와 일치하는지 확인하는 함수
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise CredentialsException()

    # make access token
    utc_now = datetime.now(timezone.utc)
    exp_time = utc_now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.name, "exp": exp_time.timestamp()}  # UNIX 타임스탬프로 변환
    access_token = jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
    }


# 매개변수로 사용한 토큰값은 OAuth2PasswordBearer에 의해 자동으로 매핑된다.
async def get_current_user_in_db(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    토큰값을 사용하여 현재 사용자 정보를 반환하는 함수
    Args:
        token: 헤더에 저장된 토큰값
        db: AsyncSession

    Returns:
        현재 사용자의 정보
    """
    from app.crud.user import get_user_in_db  # 순환 참조를 막기 위한 지연 참조

    try:
        # 토큰을 복호화하여 토큰에 담겨 있는 사용자명을 얻기 위함
        payload = jwt.decode(
            jwt=token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException()
    except (
        jwt.ExpiredSignatureError
    ):  # 사용자명이 없거나 사용자명으로 데이터 조회에 실패한 경우
        raise CredentialsException()
    else:
        user = await get_user_in_db(db, name=username)
        if user is None:
            raise CredentialsException()
        return user
