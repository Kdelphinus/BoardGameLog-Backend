import jwt

from datetime import datetime, timezone, timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.config import settings
from app.core.exceptions import CredentialsException
from app.api.dependencies import get_db, get_redis

# token 부분만 추출
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{settings.API_VERSION}/users/login"
)

# bcrypt 알고리즘을 사용하여 암호화하는 객체
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def create_token(expire_time: int, user_name: str):
    """
    token을 만드는 함수
    Args:
        expire_time: 토큰 유효 시간 (분 단위)
        user_name: 사용자 이름

    Returns:
        만든 토큰
    """
    utc_now = datetime.now(timezone.utc)

    exp = utc_now + timedelta(minutes=expire_time)
    payload = {"sub": user_name, "exp": exp.timestamp()}
    token = jwt.encode(
        payload=payload, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )

    return token


async def decode_token(token: str, detail: str = "Invalid token") -> (str, float):
    """
    토큰을 복호화하여 정상적인 토큰인지 확인하는 함수
    Args:
        token: access or refresh token
        detail: 유효 하지 않을 때, 출력될 에러 메시지

    Returns:
        토큰 주인의 이름, 토큰 만료 기간
    """
    payload = jwt.decode(
        jwt=token,
        key=settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
        options={"verify_exp": True},
    )
    username: str = payload.get("sub")
    if username is None:
        raise CredentialsException(detail=detail)

    return username, payload["exp"]


async def issue_access_token(
    db: AsyncSession, redis_db: Redis, form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    해당 사용자가 인증된 사용자인지 확인 후, 액세스 토큰과 리프레시 토큰을 발급하는 함수
    Args:
        db: AsyncSession
        redis_db: redis db
        form_data: 현재 요청 받은 데이터

    Returns:
        액세스 토큰 발급
    """
    from app.crud.user import get_user_in_db  # 순환 참조를 막기 위한 지연 참조

    # 암호화되지 않은 비밀번호를 암호화하여 데이터베이스와 일치하는지 확인하는 함수
    user = await get_user_in_db(db, form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise CredentialsException()

    # make access & refresh token
    access_token = await create_token(
        expire_time=settings.ACCESS_TOKEN_EXPIRE_MINUTES, user_name=user.name
    )
    refresh_token = await create_token(
        expire_time=settings.REFRESH_TOKEN_EXPIRE_MINUTES, user_name=user.name
    )

    # save refresh token in redis
    await redis_db.setex(
        name=f"refresh:{user.name}",
        time=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        value=refresh_token,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "name": user.name,
    }


async def reissue_access_token(refresh_token: str, redis_db: Redis):
    """
    리프레시 토큰을 사용해 다시 액세스 토큰을 발급 하는 함수
    Args:
        refresh_token: 요청 받은 리프레시 토큰
        redis_db: redis db

    Returns:
        새로운 액세스 토큰
    """
    try:
        username, _ = await decode_token(
            token=refresh_token, detail="Invalid refresh token"
        )

        # refresh token 확인
        stored_refresh_token = await redis_db.get(f"refresh:{username}")
        if stored_refresh_token != refresh_token:
            raise CredentialsException(detail="Invalid refresh token")

        # 새로운 액세스 토큰 발급
        new_access_token = await create_token(
            expire_time=settings.ACCESS_TOKEN_EXPIRE_MINUTES, user_name=username
        )

        return {"access_token": new_access_token, "token_type": "bearer"}
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsException(detail="Invalid refresh token")


async def delete_token(redis_db: Redis, token: str = Depends(oauth2_scheme)):
    """
    액세스 토큰을 무효화하고, 리프레시 토큰을 삭제하는 함수
    Args:
        redis_db: redis db
        token:

    Returns:

    """
    username, exp = await decode_token(token=token)

    try:
        await redis_db.delete(f"refresh:{username}")
        remaining_time = exp - datetime.now(timezone.utc).timestamp()
        if remaining_time > 0:
            await redis_db.setex(f"blacklist:{token}", remaining_time, "true")

        return {"message": "Successfully logged out"}
    except jwt.InvalidTokenError:
        raise CredentialsException(detail="Invalid token")


# 매개변수로 사용한 토큰값은 OAuth2PasswordBearer에 의해 자동으로 매핑된다.
async def get_current_user_in_db(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    redis_db: Redis = Depends(get_redis),
):
    """
    토큰값을 사용하여 현재 사용자 정보를 반환하는 함수
    Args:
        token: 헤더에 저장된 토큰값
        db: AsyncSession
        redis_db: redis db

    Returns:
        현재 사용자의 정보
    """
    from app.crud.user import get_user_in_db  # 순환 참조를 막기 위한 지연 참조

    try:
        # 이미 무효화 된 토큰인지 확인
        if await redis_db.get(f"blacklist:{token}"):
            raise CredentialsException("Token has been revoked")

        # 토큰을 복호화하여 토큰에 담겨 있는 사용자명을 얻기 위함
        username, _ = await decode_token(
            token=token, detail="Invalid authentication credentials: username not found"
        )
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail="Token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsException(detail="Invalid token")
    else:  # db 동작 중 발생하는 에러와 jwt 에러를 구분하기 위해 else문 사용
        user = await get_user_in_db(db, name=username)
        if user is None:
            raise CredentialsException()
        return user
