import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import status

from app.models.user import User
from test.conftest import USER_DATA, USER_DATA_LIST, USER_API_URL


async def make_check_password(user_data: USER_DATA) -> USER_DATA:
    """
    기존 사용자 데이터에 check_password 인자를 추가하는 함수
    Args:
        user_data: 생성하고자 하는 사용자 데이터

    Returns:
        check_password 가 추가된 사용자 데이터
    """
    user_data["check_password"] = user_data["password"]
    return user_data


@pytest.mark.asyncio
async def test_create_user(
    async_client: AsyncClient,
    db_session: AsyncSession,
    user_data_list: USER_DATA_LIST,
):
    """사용자 생성 테스트"""
    tmp_user = await make_check_password(user_data_list[0])

    response = await async_client.post(f"{USER_API_URL}/create", json=tmp_user)
    assert response.status_code == status.HTTP_201_CREATED

    result = await db_session.execute(select(User).where(User.name == tmp_user["name"]))
    created_user = result.scalars().first()

    assert created_user is not None
    assert created_user.email == tmp_user["email"]


@pytest.mark.asyncio
async def test_create_user_duplicate_name(
    async_client: AsyncClient,
    create_test_user: USER_DATA,
):
    """이미 존재하는 이름으로 사용자 생성 테스트"""
    create_test_user["password"] += "2"
    create_test_user["check_password"] += "2"
    create_test_user["email"] = "2" + create_test_user["email"]
    response2 = await async_client.post(f"{USER_API_URL}/create", json=create_test_user)
    assert response2.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_user_duplicate_email(
    async_client: AsyncClient,
    create_test_user: USER_DATA,
):
    """이미 존재하는 이메일로 사용자 생성 테스트"""
    create_test_user["password"] += "2"
    create_test_user["check_password"] += "2"
    create_test_user["name"] += "2"
    response2 = await async_client.post(f"{USER_API_URL}/create", json=create_test_user)
    assert response2.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_not_matched_password(
    async_client: AsyncClient, user_data_list: USER_DATA_LIST
):
    """비밀번호와 체크 비밀번호가 다를 때 사용자 생성 테스트"""
    tmp_user = await make_check_password(user_data_list[0])
    tmp_user["check_password"] += "2"

    response1 = await async_client.post(f"{USER_API_URL}/create", json=tmp_user)
    assert response1.status_code == status.HTTP_406_NOT_ACCEPTABLE


@pytest.mark.asyncio
async def test_login(
    async_client: AsyncClient,
    create_test_user: USER_DATA,
):
    """정상 로그인 테스트"""
    login_data = {
        "username": create_test_user["name"],
        "password": create_test_user["password"],
    }
    response = await async_client.post(f"{USER_API_URL}/login", data=login_data)
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert "access_token" in response
    assert "refresh_token" in response
    assert "bearer" == response["token_type"]
    assert login_data["username"] == response["name"]


@pytest.mark.asyncio
async def test_login_not_matched_password(
    async_client: AsyncClient,
    create_test_user: USER_DATA,
):
    """비밀번호가 틀릴 때 로그인 테스트"""
    login_data = {
        "username": create_test_user["name"],
        "password": create_test_user["password"] + "1",
    }
    response = await async_client.post(f"{USER_API_URL}/login", data=login_data)
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_not_existed_user(
    async_client: AsyncClient,
    create_test_user: USER_DATA,
):
    """없는 사용자일 때 로그인 테스트"""
    login_data = {
        "username": create_test_user["name"] + "1111",
        "password": create_test_user["password"],
    }
    response = await async_client.post(f"{USER_API_URL}/login", data=login_data)
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_by_refresh_token(
    async_client: AsyncClient, login_test_user: USER_DATA
):
    """리프레쉬 토큰으로 새로운 액세스 토큰을 발급받는 테스트"""
    refresh_token = login_test_user["refresh_token"]
    response = await async_client.post(
        f"{USER_API_URL}/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert response["access_token"] != login_test_user["access_token"]
    assert "bearer" == response["token_type"]


@pytest.mark.asyncio
async def test_login_by_not_matched_refresh_token(
    async_client: AsyncClient, login_test_user: USER_DATA
):
    """유효하지 않은 리프레쉬 토큰으로 새로운 액세스 토큰을 발급받는 테스트"""
    refresh_token = login_test_user["refresh_token"] + "12332"
    response = await async_client.post(
        f"{USER_API_URL}/refresh", headers={"Authorization": f"Bearer {refresh_token}"}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_logout(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """정상 로그아웃 테스트"""
    access_token = login_test_user["access_token"]
    response = await async_client.post(
        f"{USER_API_URL}/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_logout_not_matched_access_token(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """액세스 토큰이 맞지 않는 로그아웃 테스트"""
    access_token = login_test_user["access_token"] + "aaa"
    response = await async_client.post(
        f"{USER_API_URL}/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_reset_password_logout_state(
    async_client: AsyncClient, create_test_user: USER_DATA
):
    """로그아웃 한 상태에서 비밀번호 초기화를 요청하는 테스트"""
    response = await async_client.post(
        f"{USER_API_URL}/reset-password", json={"name": create_test_user["name"]}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_reset_password_login_state(
    async_client: AsyncClient, login_test_user: USER_DATA
):
    """로그인 한 상태에서 비밀번호 초기화를 요청하는 테스트"""
    response = await async_client.post(
        f"{USER_API_URL}/reset-password", json={"name": login_test_user["name"]}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_reset_password_by_not_existed_user(
    async_client: AsyncClient, create_test_user: USER_DATA
):
    """존재하지 않는 사용자의 비밀번호를 초기화하는 테스트"""
    response = await async_client.post(
        f"{USER_API_URL}/reset-password",
        json={"name": create_test_user["name"] + "222"},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_404_NOT_FOUND


# TODO 리셋 토큰이 담긴 url로 접속했을 때, 잘 동작하는지 확인하는 테스트 필요
@pytest.mark.asyncio
async def test_reset_password_confirm(
    async_client: AsyncClient, create_test_user: USER_DATA
):
    pass


@pytest.mark.asyncio
async def test_read_all_user(
    async_client: AsyncClient,
    user_data_list: USER_DATA_LIST,
    create_test_user_list: None,
):
    """사용자 목록을 가져 오는 테스트"""
    response = await async_client.get(f"{USER_API_URL}/list")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(user_data_list)


@pytest.mark.asyncio
async def test_read_me(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """로그인한 유저의 정보를 가져 오는 테스트"""
    access_token = login_test_user["access_token"]
    response = await async_client.get(
        f"{USER_API_URL}/list/me", headers={f"Authorization": f"Bearer {access_token}"}
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert response["name"] == login_test_user["name"]


@pytest.mark.asyncio
async def test_read_me_not_matched_access_token(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """맞지 않는 액세스 토큰으로 현재 유저 정보를 가져 오는 테스트"""
    access_token = login_test_user["access_token"] + "1"
    response = await async_client.get(
        f"{USER_API_URL}/list/me", headers={f"Authorization": f"Bearer {access_token}"}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_read_user(
    async_client: AsyncClient,
    user_data_list: USER_DATA_LIST,
    create_test_user_list: None,
):
    """사용자 이름으로 특정 사용자의 정보를 가져 오는 테스트"""
    user_data = user_data_list[0]
    response = await async_client.get(f"{USER_API_URL}/list/{user_data["name"]}")
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert response["name"] == user_data["name"]
    assert response["email"] == user_data["email"]


@pytest.mark.asyncio
async def test_read_not_existed_user(
    async_client: AsyncClient,
    user_data_list: USER_DATA_LIST,
    create_test_user_list: None,
):
    """존재하지 않는 특정 사용자의 정보를 가져 오는 테스트"""
    user_data = user_data_list[0]
    response = await async_client.get(f"{USER_API_URL}/list/{user_data["name"] + "aa"}")
    status_code = response.status_code

    assert status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_change_email(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """이메일을 수정을 테스트하는 함수"""
    change_ameil = "changemail@exam.com"
    response = await async_client.patch(
        f"{USER_API_URL}/patch",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        json={"email": change_ameil},
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert login_test_user["name"] == response["name"]
    assert change_ameil == response["email"]

    response = await async_client.get(
        f"{USER_API_URL}/list/me",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    current_email = response.json()["email"]

    assert current_email == change_ameil


@pytest.mark.asyncio
async def test_cannot_modify_immutable_field(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """바꿀 수 없는 속성을 바꾸는 테스트"""
    response = await async_client.patch(
        f"{USER_API_URL}/patch",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        json={"name": "change_user"},
    )

    status_code = response.status_code

    assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_cannot_update_nonexistent_field(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """없는 속성을 바꾸는 테스트"""
    response = await async_client.patch(
        f"{USER_API_URL}/patch",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        json={"no existed attribute": "change_user"},
    )

    status_code = response.status_code

    assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_with_identical_data(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
):
    """기존과 동일한 데이터로 바꾸는 테스트"""
    response = await async_client.get(
        f"{USER_API_URL}/list/me",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    current_email = response.json()["email"]

    response = await async_client.patch(
        f"{USER_API_URL}/patch",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        json={"email": current_email},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_deactivate_user_login_state(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,
):
    """로그인 한 상태에서 사용자 soft delete"""
    response = await async_client.patch(
        f"{USER_API_URL}/deactivate",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_200_OK

    # 로그아웃 확인
    response = await async_client.get(
        f"{USER_API_URL}/list/me",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # 유저 비활성화 확인
    response = await async_client.get(f"{USER_API_URL}/list/{login_test_user["name"]}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

    response = await async_client.get(f"{USER_API_URL}/list")
    response = response.json()
    for n, e in response:
        assert n != login_test_user["name"]

    response = await async_client.get(
        f"{USER_API_URL}/list/deactivate",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    response = response.json()
    assert len(response) == 1


@pytest.mark.asyncio
async def test_deactivate_user_logout_state(
    async_client: AsyncClient,
    logout_test_user: USER_DATA,
):
    """로그아웃 한 상태에서 사용자 soft delete"""
    response = await async_client.patch(
        f"{USER_API_URL}/deactivate",
        headers={f"Authorization": f"Bearer {logout_test_user["access_token"]}"},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_restore_user_logout_state(
    async_client: AsyncClient, login_test_user: USER_DATA
):
    """로그아웃 한 상태에서 사용자 복원을 요청하는 테스트"""
    await async_client.patch(
        f"{USER_API_URL}/deactivate",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )

    response = await async_client.post(
        f"{USER_API_URL}/restore", json={"name": login_test_user["name"]}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_restore_not_exsited_user_logout_state(async_client: AsyncClient):
    """없는 사용자 복원을 요청하는 테스트"""
    response = await async_client.post(
        f"{USER_API_URL}/restore", json={"name": "not_existed_user_name"}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_restore_user_login_state(
    async_client: AsyncClient, login_test_user: USER_DATA
):
    """로그인 한 상태에서 사용자 복원을 요청하는 테스트"""
    response = await async_client.post(
        f"{USER_API_URL}/restore", json={"name": login_test_user["name"]}
    )
    status_code = response.status_code

    assert status_code == status.HTTP_404_NOT_FOUND


# TODO 리스토어 토큰이 담긴 url로 접속했을 때, 잘 동작하는지 확인하는 테스트 필요
@pytest.mark.asyncio
async def test_restore_user_confirm(
    async_client: AsyncClient, create_test_user: USER_DATA
):
    pass
