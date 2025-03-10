import os, jwt
from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from database import get_db
from domain.user import user_crud, user_schema
from domain.user.user_crud import pwd_context

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 토큰 유효기간, 분 단위 설정
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"  # 토큰 생성 시 사용하는 알고리즘
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{os.getenv("API_VERSION")}/user/login"
)

router = APIRouter(prefix=f"/api/{os.getenv("API_VERSION")}/user")


@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
async def create_user(
    _user_info: user_schema.UserCreate, db: AsyncSession = Depends(get_db)
):
    user = await user_crud.get_existing_user(db, user_info=_user_info)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="이미 존재하는 사용자입니다."
        )
    await user_crud.create_user(db=db, user_info=_user_info)


@router.post("/login", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    # check user and password
    user = await user_crud.get_user(db, form_data.username)
    # verify 함수는 암호화되지 않은 비밀번호를 암호화하여 데이터베이스와 일치하는지 확인하는 함수
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,  # 인증 오류
            detail="Incorrect name or password",
            headers={"WWW-Authenticate": "Bearer"},  # 인증 방식에 대한 추가 정보
        )

    # make access token
    utc_now = datetime.now(timezone.utc)
    exp_time = utc_now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.name, "exp": exp_time.timestamp()}  # UNIX 타임스탬프로 변환
    access_token = jwt.encode(payload=payload, key=SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "name": user.name,
    }


# 헤더 정보의 토큰값을 읽어 사용자 객체를 리턴하는 함수
# 매개변수로 사용한 토큰값은 OAuth2PasswordBearer에 의해 자동으로 매핑된다.
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # 토큰을 복호화하여 토큰에 담겨 있는 사용자명을 얻기 위함
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except (
        jwt.ExpiredSignatureError
    ):  # 사용자명이 없거나 사용자명으로 데이터 조회에 실패한 경우
        raise credentials_exception
    else:
        user = await user_crud.get_user(db, name=username)
        if user is None:
            raise credentials_exception
        return user


# TODO 개발을 위한 임시 API
@router.get("/list/all", status_code=status.HTTP_200_OK)
async def get_all_user(db: AsyncSession = Depends(get_db)):
    return await user_crud.get_all_user(db)
