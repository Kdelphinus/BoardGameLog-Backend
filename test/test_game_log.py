import pytest, json
from httpx import AsyncClient
from fastapi import status

from test.conftest import (
    USER_DATA,
    GAME_DATA,
    GAME_DATA_LIST,
    GAME_LOG_DATA,
    GAME_LOG_DATA_LIST,
    GAME_LOG_API_URL,
    login_test_user,
    logout_test_user,
)


@pytest.mark.asyncio
async def test_create_game_log(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game: GAME_DATA_LIST,
    game_log_data_list: GAME_LOG_DATA_LIST,
):
    """게임 기록 생성 테스트"""
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data_list[0],
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_create_game_log_no_permission(
    async_client: AsyncClient,
    create_test_all_game: GAME_DATA_LIST,
    game_log_data_list: GAME_LOG_DATA_LIST,
):
    """로그인하지 않은 사용자가 게임 기록을 생성하려고 할 때"""
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data_list[0],
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_game_log_invalid_data(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game: GAME_DATA_LIST,
    game_log_data_list: GAME_LOG_DATA_LIST,
):
    """게임 기록 생성 데이터가 잘못 되었을 때"""
    game_log_data = game_log_data_list[0]

    # 참석 인원이 잘못 되었을 때
    game_log_data["participant_num"] = 0
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data,
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # 없는 게임을 기록하려 할 때
    game_log_data["participant_num"] = 2
    game_log_data["game_name"] = "없는 게임"
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data,
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # 제목이 없을 때
    game_log_data["game_name"] = "캐스캐디아"
    game_log_data["subject"] = ""
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data,
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE

    # 소요 시간이 잘못되었을 때
    game_log_data["subject"] = "임시 제목"
    game_log_data["during_time"] = 0
    response = await async_client.post(
        f"{GAME_LOG_API_URL}/create",
        json=game_log_data,
        headers={f"Authorization": f"Bearer {login_test_user["access_token"]}"},
    )
    assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE


@pytest.mark.asyncio
async def test_read_all_game_log(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """전체 게임 기록을 가져오는 테스트"""
    response = await async_client.get(f"{GAME_LOG_API_URL}/list")
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert (
        len(response) == len(create_test_all_game_log[1]) * 2
    )  # 게임 기록을 중복으로 생성했음


async def test_read_my_game_log(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """내가 작성한 게임 기록을 가져오는 테스트"""
    test_user = create_test_all_game_log[0]
    my_game_log_data = create_test_all_game_log[1]

    response = await async_client.get(
        f"{GAME_LOG_API_URL}/list/my",
        headers={f"Authorization": f"Bearer {test_user["access_token"]}"},
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert len(response) == len(my_game_log_data)
    for res in response:
        assert res["user_name"] == test_user["name"]


async def test_read_my_game_log_no_permission(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """권한이 없을 때"""
    response = await async_client.get(f"{GAME_LOG_API_URL}/list/my")
    status_code = response.status_code

    assert status_code == status.HTTP_401_UNAUTHORIZED


async def test_read_game_log_one_game(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """하나의 게임 기록을 가져오는 테스트"""
    test_user = create_test_all_game_log[0]
    game_log_data = create_test_all_game_log[1]

    response = await async_client.get(
        f"{GAME_LOG_API_URL}/list/{game_log_data[0]["game_name"]}",
        headers={f"Authorization": f"Bearer {test_user["access_token"]}"},
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert len(response) == len(game_log_data)
    for res in response:
        assert res["game_name"] == game_log_data[0]["game_name"]


async def test_read_game_log_not_exsited_game(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """없는 게임 기록을 가져오는 테스트"""
    test_user = create_test_all_game_log[0]
    game_log_data = create_test_all_game_log[1]

    response = await async_client.get(
        f"{GAME_LOG_API_URL}/list/{game_log_data[0]["game_name"] + "a"}",
        headers={f"Authorization": f"Bearer {test_user["access_token"]}"},
    )
    status_code = response.status_code

    assert status_code == status.HTTP_404_NOT_FOUND


async def test_read_my_game_log_one_game(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """나의 게임 기록 중 하나의 게임 기록을 가져오는 테스트"""
    test_user = create_test_all_game_log[0]
    game_log_data = create_test_all_game_log[1]

    response = await async_client.get(
        f"{GAME_LOG_API_URL}/list/my/{game_log_data[0]["game_name"]}",
        headers={f"Authorization": f"Bearer {test_user["access_token"]}"},
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert len(response) == 1
    assert response[0]["game_name"] == game_log_data[0]["game_name"]


async def test_update_game_log(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """나의 게임 기록 수정"""
    test_user = create_test_all_game_log[0]

    response = await async_client.patch(
        f"{GAME_LOG_API_URL}/patch/my/1",
        headers={f"Authorization": f"Bearer {test_user['access_token']}"},
        json={
            "subject": "change subject",
            "game_name": "아크노바",
            "during_time": 80,
        },
    )
    status_code = response.status_code
    response = response.json()

    assert status_code == status.HTTP_200_OK
    assert response["subject"] == "change subject"
    assert response["game_name"] == "아크노바"
    assert response["during_time"] == 80


async def test_update_game_log_no_permission(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """다른 사람 기록을 수정하려 했을 때"""
    test_user = create_test_all_game_log[0]

    response = await async_client.patch(
        f"{GAME_LOG_API_URL}/patch/my/2",
        headers={f"Authorization": f"Bearer {test_user['access_token']}"},
        json={
            "subject": "change subject",
            "game_name": "아크노바",
            "during_time": 80,
        },
    )
    status_code = response.status_code
    assert status_code == status.HTTP_403_FORBIDDEN


async def test_delete_game_log(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """게임 기록을 삭제하는 테스트"""
    test_user = create_test_all_game_log[0]
    game_log_data = create_test_all_game_log[1]

    response = await async_client.delete(
        f"{GAME_LOG_API_URL}/delete/my/1",
        headers={f"Authorization": f"Bearer {test_user['access_token']}"},
    )
    status_code = response.status_code
    assert status_code == status.HTTP_200_OK

    response = await async_client.get(
        f"{GAME_LOG_API_URL}/list/my",
        headers={f"Authorization": f"Bearer {test_user['access_token']}"},
    )
    response = response.json()

    assert len(response) == len(game_log_data) - 1


async def test_delete_game_log_no_permission(
    async_client: AsyncClient,
    create_test_all_game_log: (USER_DATA, GAME_DATA_LIST),
):
    """남의 게임 기록을 삭제하는 테스트"""
    test_user = create_test_all_game_log[0]

    response = await async_client.delete(
        f"{GAME_LOG_API_URL}/delete/my/2",
        headers={f"Authorization": f"Bearer {test_user['access_token']}"},
    )
    status_code = response.status_code
    assert status_code == status.HTTP_403_FORBIDDEN
