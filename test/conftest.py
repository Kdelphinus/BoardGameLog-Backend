import pytest
from typing import Any
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base
from app.config import settings
from app.api.dependencies import get_db
from app.models.user import User
from app.core.security import pwd_context


USER_DATA = dict[str, str]
USER_DATA_LIST = list[USER_DATA]
GAME_DATA = dict[str, Any]
GAME_DATA_LIST = list[GAME_DATA]
GAME_LOG_DATA = dict[str, Any]
GAME_LOG_DATA_LIST = list[GAME_LOG_DATA]

BASIC_API_URL = f"/api/{settings.API_VERSION}"
USER_API_URL = f"{BASIC_API_URL}/users"
GAME_API_URL = f"{BASIC_API_URL}/games"
GAME_LOG_API_URL = f"{BASIC_API_URL}/game_logs"


@pytest.fixture(scope="function")
async def db_session():
    """
    테스트 용 db session을 생성하여 반환하는 함수
    Returns:
        AsyncSession
    """
    # SQLite 메모리 데이터베이스 사용 (테스트마다 초기화)
    engine = create_async_engine(
        settings.TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 테스트 세션 생성
    TestAsyncSessionLocal = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    # 테스트 후 데이터베이스 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def async_client():
    """
    테스트 할 비동기 클라이언트를 반환하는 함수
    Returns:
        AsyncClient
    """
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest.fixture(autouse=True)
def override_get_async_session(db_session: AsyncSession):
    """
    종속 함수를 테스트 용으로 변환하는 함수
    Args:
        db_session: 테스트 용 AsyncSession

    Returns:
        실제 종속성 함수 대신 테스트 용 종속성 함수 반환
    """

    async def _override_get_async_session():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_async_session


@pytest.fixture(scope="function")
def user_data_list() -> USER_DATA_LIST:
    """
    테스트 사용자 데이터를 반환하는 함수
    Returns:
       default, login, update, reset 유저 데이터가 dictionary 로 반환
    """
    return [
        {
            "name": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
        },
        {
            "name": "loginuser",
            "email": "login@example.com",
            "password": "loginpassword123",
        },
        {
            "name": "updateuser",
            "email": "update@example.com",
            "password": "updatepassword123",
        },
        {
            "name": "resetuser",
            "email": "reset@example.com",
            "password": "oldpassword123",
        },
    ]


@pytest.fixture(scope="function")
def admin_data() -> USER_DATA:
    """
    테스트 관리자 데이터를 반환하는 함수
    Returns:
       관리자 데이터가 dictionary 로 반환
    """
    return {
        "name": "testadmin",
        "email": "testadmin@example.com",
        "password": "Testadminpassword123",
    }


@pytest.fixture(scope="function")
def game_data_list() -> GAME_DATA_LIST:
    """
    테스트 용 게임 데이터를 반환하는 함수
    Returns:
        게임 데이터가 dictionary 리스트로 반환
    """
    return [
        {
            "name": "캐스캐디아",
            "weight": 1.97,
            "min_possible_num": 1,
            "max_possible_num": 4,
        },
        {
            "name": "아크노바",
            "weight": 3.97,
            "min_possible_num": 1,
            "max_possible_num": 4,
        },
    ]


@pytest.fixture(scope="function")
def game_log_data_list() -> GAME_LOG_DATA_LIST:
    """
    테스트 용 게임 기록 데이터를 반환하는 함수
    Returns:
        게임 기록 데이터가 dictionary 리스트로 반환
    """
    return [
        {
            "game_name": "캐스캐디아",
            "during_time": 30,
            "participant_num": 2,
            "subject": "캐스캐디아 첫 판",
            "content": "구성물들이 이쁘다",
        },
        {
            "game_name": "아크노바",
            "during_time": 180,
            "participant_num": 2,
            "subject": "아크노바 첫 판",
            "content": "동물원 만들기 재밌다",
        },
    ]


@pytest.fixture(scope="function")
async def create_test_user_list(
    async_client: AsyncClient, user_data_list: USER_DATA_LIST
) -> None:
    """
    테스트 사용자 목록에 있는 모든 유저를 db에 저장하는 함수
    Args:
        async_client: AsyncClient
        user_data_list: 사용자 데이터 리스트

    Returns:
        None
    """
    for user_data in user_data_list:
        user_data["check_password"] = user_data["password"]
        await async_client.post(f"{USER_API_URL}/create", json=user_data)


@pytest.fixture(scope="function")
async def create_test_user(
    async_client: AsyncClient, user_data_list: USER_DATA_LIST
) -> USER_DATA:
    """
    테스트용 사용자 정보로 사용자 생성
    Args:
        async_client: AsyncClient
        user_data_list: 테스트용 사용자 데이터 리스트

    Returns:
        생성된 사용자의 정보
    """
    user_data = user_data_list[0]
    user_data["check_password"] = user_data["password"]
    await async_client.post(f"{USER_API_URL}/create", json=user_data)
    return user_data_list[0]


@pytest.fixture(scope="function")
async def login_test_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
    create_test_user: USER_DATA,
) -> USER_DATA:
    """
    테스트용 사용자로 로그인
    Args:
        async_client: AsyncClient
        db_session: AsyncSession
        create_test_user: 테스트용 사용자를 생성하는 함수

    Returns:
        로그인 한 사용자의 정보 반환
        key = ["access_token", "refresh_token", "token_type", "name"]
    """
    login_data = {
        "username": create_test_user["name"],
        "password": create_test_user["password"],
    }
    response = await async_client.post(f"{USER_API_URL}/login", data=login_data)
    return response.json()


@pytest.fixture(scope="function")
async def logout_test_user(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
) -> USER_DATA:
    """
    로그아웃 한 사용자의 정보를 반환하는 함수
    Args:
        async_client: AsyncClient
        login_test_user: USER DATA

    Returns:
        로그아웃 한 사용자의 정보 반환
        key = ["access_token", "refresh_token", "token_type", "name"]
    """
    access_token = login_test_user["access_token"]
    await async_client.post(
        f"{USER_API_URL}/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    return login_test_user


@pytest.fixture(scope="function")
async def create_admin_user(db_session: AsyncSession, admin_data: USER_DATA):
    """테스트 용 관리자 계정을 생성하는 함수"""
    admin_user = User(
        name=admin_data["name"],
        email=admin_data["email"],
        password=pwd_context.hash(admin_data["password"]),
        is_admin=True,
    )
    db_session.add(admin_user)
    await db_session.commit()
    await db_session.refresh(admin_user)
    return admin_data


@pytest.fixture(scope="function")
async def login_admin_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
    create_admin_user: USER_DATA,
) -> USER_DATA:
    """
    테스트용 사용자로 로그인
    Args:
        async_client: AsyncClient
        db_session: AsyncSession
        create_admin_user: 테스트용 관리자를 생성하는 함수

    Returns:
        로그인 한 사용자의 정보 반환
        key = ["access_token", "refresh_token", "token_type", "name"]
    """
    login_data = {
        "username": create_admin_user["name"],
        "password": create_admin_user["password"],
    }
    response = await async_client.post(f"{USER_API_URL}/login", data=login_data)
    return response.json()


@pytest.fixture(scope="function")
async def create_test_game(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    game_data_list: GAME_DATA_LIST,
) -> GAME_DATA:
    """
    임시 게임 정보를 생성하는 함수
    Args:
        async_client: AsyncClient
        login_admin_user: 관리자 계정
        game_data_list: 임시 게임 정보 리스트

    Returns:
        생성된 게임의 정보
    """
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=game_data_list[0],
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    return game_data_list[0]


@pytest.fixture(scope="function")
async def create_test_all_game(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    game_data_list: GAME_DATA_LIST,
) -> GAME_DATA_LIST:
    """
    임시 게임 정보를 생성하는 함수
    Args:
        async_client: AsyncClient
        login_admin_user: 관리자 계정
        game_data_list: 임시 게임 정보 리스트

    Returns:
        생성된 게임의 정보
    """
    for tmp_game_data in game_data_list:
        await async_client.post(
            f"{GAME_API_URL}/create",
            json=tmp_game_data,
            headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
        )
    return game_data_list


@pytest.fixture(scope="function")
async def create_test_all_game_log(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,
    create_test_all_game: GAME_DATA_LIST,
    game_log_data_list: GAME_LOG_DATA_LIST,
) -> (USER_DATA, GAME_LOG_DATA_LIST):
    """
    임시 게임 기록을 생성하는 함수
    Args:
        async_client: AsyncClient
        login_test_user: 사용자 계정
        login_admin_user: 관리자 계정
        create_test_all_game: 만들 게임 기록
        game_log_data_list: 임시 게임 기록

    Returns:
        기록을 생성한 유저, 생성된 게임 기록 리스트
    """
    for tmp_game_log_data in game_log_data_list:
        await async_client.post(
            f"{GAME_LOG_API_URL}/create",
            json=tmp_game_log_data,
            headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        )
        await async_client.post(
            f"{GAME_LOG_API_URL}/create",
            json=tmp_game_log_data,
            headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
        )
    return login_test_user, game_log_data_list
