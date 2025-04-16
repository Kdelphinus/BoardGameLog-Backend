import pytest
from httpx import AsyncClient
from fastapi import status

from test.conftest import (
    USER_DATA,
    GAME_DATA,
    GAME_DATA_LIST,
    GAME_API_URL,
    login_admin_user,
)


@pytest.mark.asyncio
async def test_create_game(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    game_data_list: GAME_DATA_LIST,
):
    """게임 정보 생성 테스트"""
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=game_data_list[0],
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asynico
async def test_create_game_duplicate_name(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """이미 존재하는 이름으로 게임 생성 테스트"""
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=create_test_game,
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_create_game_no_permission(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    game_data_list: GAME_DATA_LIST,
):
    """게임 정보 생성 권한이 없을 때 생성 테스트"""
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=game_data_list[0],
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asynico
async def test_create_game_invalid_data(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """이미 존재하는 이름으로 게임 생성 테스트"""
    create_test_game["weight"] = -1
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=create_test_game,
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    create_test_game["weight"] = 1
    create_test_game["min_possible_num"] = create_test_game["max_possible_num"] + 1
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=create_test_game,
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    create_test_game["min_possible_num"] = -1
    create_test_game["max_possible_num"] = 4
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=create_test_game,
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    create_test_game["min_possible_num"] = 1
    create_test_game["name"] = ""
    response = await async_client.post(
        f"{GAME_API_URL}/create",
        json=create_test_game,
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asynico
async def test_read_all_game(
    async_client: AsyncClient,
    create_test_all_game: GAME_DATA_LIST,
    game_data_list: GAME_DATA_LIST,
):
    """전체 게임 목록을 불러오는 테스트"""
    response = await async_client.get(f"{GAME_API_URL}/list")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(game_data_list)


@pytest.mark.asynico
async def test_read_game(
    async_client: AsyncClient,
    create_test_all_game: GAME_DATA_LIST,
    game_data_list: GAME_DATA_LIST,
):
    """특정 게임의 정보를 불러오는 테스트"""
    game_data = game_data_list[0]
    response = await async_client.get(f"{GAME_API_URL}/list/{game_data["name"]}")
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert response["name"] == game_data["name"]
    assert response["weight"] == game_data["weight"]
    assert response["min_possible_num"] == game_data["min_possible_num"]
    assert response["max_possible_num"] == game_data["max_possible_num"]


@pytest.mark.asynico
async def test_read_not_existed_game(
    async_client: AsyncClient,
    create_test_all_game: GAME_DATA_LIST,
    game_data_list: GAME_DATA_LIST,
):
    """없는 게임 목록을 불러오는 테스트"""
    game_data = game_data_list[0]
    response = await async_client.get(f"{GAME_API_URL}/list/{game_data["name"] + "a"}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asynico
async def test_update_game_data(
    async_client: AsyncClient,
    create_test_game: GAME_DATA,
    login_admin_user: USER_DATA,
):
    """게임 정보를 수정하는 테스트"""
    response = await async_client.patch(
        f"{GAME_API_URL}/patch/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
        json={
            "weight": create_test_game["weight"] + 1,
            "min_possible_num": 2,
            "max_possible_num": 6,
        },
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert create_test_game["weight"] + 1 == response["weight"]
    assert 2 == response["min_possible_num"]
    assert 6 == response["max_possible_num"]


@pytest.mark.asynico
async def test_update_game_data_no_permission(
    async_client: AsyncClient,
    create_test_game: GAME_DATA,
    login_test_user: USER_DATA,
):
    """게임 정보를 수정 권한이 없을 때 수정하는 테스트"""
    response = await async_client.patch(
        f"{GAME_API_URL}/patch/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
        json={
            "weight": create_test_game["weight"] + 1,
            "min_possible_num": 2,
            "max_possible_num": 6,
        },
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_cannot_update_nonexistent_field(
    async_client: AsyncClient,
    create_test_game: GAME_DATA,
    login_admin_user: USER_DATA,
):
    """없는 속성을 바꾸는 테스트"""
    response = await async_client.patch(
        f"{GAME_API_URL}/patch/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
        json={"no existed attribute": "change_user"},
    )

    status_code = response.status_code

    assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_update_with_identical_data(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """기존과 동일한 데이터로 바꾸는 테스트"""
    response = await async_client.patch(
        f"{GAME_API_URL}/patch/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_game(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """게임 정보를 삭제하는 테스트"""
    response = await async_client.delete(
        f"{GAME_API_URL}/delete/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    status_code = response.status_code
    assert status_code == status.HTTP_200_OK

    response = await async_client.get(f"{GAME_API_URL}/list")
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_delete_game_not_existed_game(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """없는 게임 정보를 삭제하는 테스트"""
    response = await async_client.delete(
        f"{GAME_API_URL}/delete/{create_test_game["name"]} + a",
        headers={f"Authorization": f"Bearer {login_admin_user["access_token"]}"},
    )
    status_code = response.status_code
    assert status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_game_no_permission(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_game: GAME_DATA,
):
    """게임 정보를 삭제하는 권한이 없을 때 테스트"""
    response = await async_client.delete(
        f"{GAME_API_URL}/delete/{create_test_game["name"]}",
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    status_code = response.status_code
    assert status_code == status.HTTP_403_FORBIDDEN
