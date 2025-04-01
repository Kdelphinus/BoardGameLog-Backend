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
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"verify_exp": True},
        )
        username: str = payload.get("sub")
        if username is None:
            raise CredentialsException(detail=detail)
    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsException(detail=f"Invalid token {token}")

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


async def delete_token(redis_db: Redis, token: str):
    """
    액세스 토큰을 무효화하고, 리프레시 토큰을 삭제하는 함수
    Args:
        redis_db: redis db
        token:

    Returns:

    """
    username, exp = await decode_token(token=token)

    await redis_db.delete(f"refresh:{username}")
    remaining_time = exp - datetime.now(timezone.utc).timestamp()
    if remaining_time > 0:
        await redis_db.setex(f"blacklist:{token}", int(remaining_time), "true")

    return {"message": "Successfully logged out"}


async def send_reset_password_email(name: str, email: str):
    """
    비밀번호 재설정 링크를 보내는 함수
    Args:
        name: 사용자의 이름
        email: 사용자의 이메일

    Returns:
        추후 -> 이메일을 발송했다는 메시지
    """
    reset_token = await create_token(expire_time=30, user_name=name)

    # TODO 프론트 url 연결 해야 함
    # reset_link = f"https://boardgamelog.com/reset-password?token={reset_token}"
    # await send_email(email=email, "Reset your password", f"Click the link: {reset_link}")
    return {"message": "Password reset email sent"}


async def reset_password(token: str, new_password: str, db: AsyncSession):
    """
    비밀번호를 재설정하는 함수
    Args:
        token: reset token
        new_password: 새로운 비밀번호
        db: AsyncSession

    Returns:
        비밀번호가 재설정되었다는 메시지
    """
    from app.crud.user import (
        get_user_in_db,
        update_user_in_db,
    )  # 순환 참조를 막기 위한 지연 참조

    username, _ = await decode_token(token)
    user = await get_user_in_db(db=db, name=username)
    if not user:
        raise CredentialsException()
    update_data = {"password": pwd_context.hash(new_password)}
    await update_user_in_db(db=db, user=user, update_data=update_data)

    return {"message": "Password has been reset"}


async def send_restore_email(name: str, email: str):
    """
    휴면 사용자를 복구 하는 링크를 보내는 함수
    Args:
        name: 사용자의 이름
        email: 사용자의 이메일

    Returns:
        이메일을 발송했다는 메시지
    """
    restore_token = await create_token(expire_time=30, user_name=name)

    # TODO 프론트 url 연결 해야 함
    # restore_link = f"https://boardgamelog.com/reset-password?token={restore_token}"
    # await send_email(email=email, "Restore your account", f"Click the link: {restore_link}")
    return {"message": "Restore email sent"}


async def restore_user(token: str, db: AsyncSession):
    """
    휴면 사용자를 복구하는 함수
    Args:
        token: restore token
        db: AsyncSession

    Returns:
        사용자가 복구되었다는 메시지
    """
    from app.crud.user import (
        get_user_in_db,
        update_user_in_db,
    )  # 순환 참조를 막기 위한 지연 참조

    username, _ = await decode_token(token)
    user = await get_user_in_db(db=db, name=username)
    if not user:
        raise CredentialsException()
    update_data = {"is_deleted": False, "deleted_at": None}
    await update_user_in_db(db=db, user=user, update_data=update_data)

    return {"message": f"{username} has been restored"}


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

    # 이미 무효화 된 토큰인지 확인
    if await redis_db.get(f"blacklist:{token}"):
        raise CredentialsException("Token has been revoked")

    # 토큰을 복호화하여 토큰에 담겨 있는 사용자명을 얻기 위함
    username, _ = await decode_token(
        token=token, detail="Invalid authentication credentials: username not found"
    )
    user = await get_user_in_db(db, name=username)
    if user is None:
        raise CredentialsException()
    return user
