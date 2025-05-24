from typing import Tuple  # For type hinting fixture return values

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select  # For direct DB queries
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)  # For db_session type hint and direct queries

from app.config import settings
from app.models.game_log_like import GameLogLike as GameLogLikeModel
from test.conftest import (
    USER_DATA,
    GAME_LOG_DATA_LIST,
    GAME_LOG_LIKE_API_URL,
    USER_API_URL,
    USER_DATA_LIST,  # For user login in pagination test
)


# Note: The create_test_all_game_log fixture creates game logs.
# If game_log_data_list (from conftest) has 2 items:
# Game Log ID 1: game_log_data_list[0] by login_test_user (name: "testuser")
# Game Log ID 2: game_log_data_list[0] by login_admin_user (name: "testadmin")
# Game Log ID 3: game_log_data_list[1] by login_test_user
# Game Log ID 4: game_log_data_list[1] by login_admin_user
# Most tests will use game_log_id = 1 and login_test_user.


@pytest.mark.asyncio
async def test_create_like_success(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test successfully creating a like for a game log."""
    game_log_id_to_like = 1
    access_token = login_test_user["access_token"]

    response = await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_to_like}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"message": "Successfully liked the game log"}

    # Verify with /is_liked endpoint
    check_response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{game_log_id_to_like}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert check_response.status_code == status.HTTP_200_OK
    assert check_response.json() == {"is_liked": True}


@pytest.mark.asyncio
async def test_create_like_already_exists(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test attempting to create a like that already exists (should suggest PATCH)."""
    game_log_id_to_like = 1
    access_token = login_test_user["access_token"]

    # First like
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_to_like}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    # Try to like again
    response = await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_to_like}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["message"] == "Like operation requested"
    assert content["action"] == "PATCH"
    assert content["game_log_id"] == game_log_id_to_like
    assert (
        content["endpoint"]
        == f"/api/{settings.API_VERSION}/game_log_like/update/{game_log_id_to_like}"
    )


@pytest.mark.asyncio
async def test_create_like_non_existent_game_log(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test creating a like for a non-existent game log."""
    non_existent_game_log_id = 9999
    access_token = login_test_user["access_token"]

    response = await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{non_existent_game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"Game log [{non_existent_game_log_id}] is not found."
    }


@pytest.mark.asyncio
async def test_create_like_no_auth(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test creating a like without authentication."""
    game_log_id_to_like = 1
    response = await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_to_like}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_check_is_liked_true(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test checking like status when user has liked."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_liked": True}


@pytest.mark.asyncio
async def test_check_is_liked_false_after_unlike(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test checking like status after a user unlikes a post."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_liked": False}


@pytest.mark.asyncio
async def test_check_is_liked_false_no_interaction(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test checking like status when user has not interacted."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_liked": False}


@pytest.mark.asyncio
async def test_check_is_liked_non_existent_game_log(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test checking like status for a non-existent game log."""
    non_existent_game_log_id = 9999
    access_token = login_test_user["access_token"]
    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{non_existent_game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"is_liked": False}


@pytest.mark.asyncio
async def test_check_is_liked_no_auth(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test checking like status without authentication."""
    game_log_id = 1
    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/is_liked/{game_log_id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_get_like_list_with_likes(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,  # Using admin as a second distinct user
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test getting a list of likes for a game log."""
    game_log_id = 1
    user1_token = login_test_user["access_token"]
    user1_name = login_test_user["name"]
    user2_token = login_admin_user["access_token"]
    user2_name = login_admin_user["name"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )

    response = await async_client.get(f"{GAME_LOG_LIKE_API_URL}/list/{game_log_id}")
    assert response.status_code == status.HTTP_200_OK
    likes_list = response.json()
    assert len(likes_list) == 2
    user_names_who_liked = sorted([like["user_name"] for like in likes_list])
    assert user_names_who_liked == sorted([user1_name, user2_name])


@pytest.mark.asyncio
async def test_get_like_list_no_likes(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test getting list of likes when there are none."""
    game_log_id = 1
    response = await async_client.get(f"{GAME_LOG_LIKE_API_URL}/list/{game_log_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_like_list_active_and_inactive_likes(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test list only returns active likes."""
    game_log_id = 1
    user1_token = login_test_user["access_token"]
    user1_name = login_test_user["name"]
    user2_token = login_admin_user["access_token"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )  # User2 unlikes

    response = await async_client.get(f"{GAME_LOG_LIKE_API_URL}/list/{game_log_id}")
    assert response.status_code == status.HTTP_200_OK
    likes_list = response.json()
    assert len(likes_list) == 1
    assert likes_list[0]["user_name"] == user1_name


@pytest.mark.asyncio
async def test_get_like_list_non_existent_game_log(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test getting list of likes for a non-existent game log."""
    non_existent_game_log_id = 9999
    response = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/list/{non_existent_game_log_id}"
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_like_list_pagination(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,
    user_data_list: USER_DATA_LIST,
    create_test_user_list: None,  # Creates users from user_data_list fixture
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test pagination for the list of likes."""
    game_log_id = 1
    user1_token = login_test_user["access_token"]
    user1_name = login_test_user["name"]
    user2_token = login_admin_user["access_token"]
    user2_name = login_admin_user["name"]

    # loginuser (user_data_list[1]) as user3
    user3_login_data = user_data_list[1]
    login_resp = await async_client.post(
        f"{USER_API_URL}/login",
        data={
            "username": user3_login_data["name"],
            "password": user3_login_data["password"],
        },
    )
    assert login_resp.status_code == status.HTTP_200_OK
    user3_token = login_resp.json()["access_token"]
    user3_name = user3_login_data["name"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user1_token}"},
    )
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user2_token}"},
    )
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {user3_token}"},
    )

    response_page1 = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/list/{game_log_id}?skip=0&limit=2"
    )
    assert response_page1.status_code == status.HTTP_200_OK
    likes_page1 = response_page1.json()
    assert len(likes_page1) == 2

    response_page2 = await async_client.get(
        f"{GAME_LOG_LIKE_API_URL}/list/{game_log_id}?skip=2&limit=2"
    )
    assert response_page2.status_code == status.HTTP_200_OK
    likes_page2 = response_page2.json()
    assert len(likes_page2) == 1

    all_retrieved_likers = sorted(
        [like["user_name"] for like in likes_page1]
        + [like["user_name"] for like in likes_page2]
    )
    expected_likers = sorted([user1_name, user2_name, user3_name])
    assert all_retrieved_likers == expected_likers


@pytest.mark.asyncio
async def test_update_like_toggle_to_false(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test updating a like (toggling flag to False)."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    response = await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    updated_like = response.json()
    assert updated_like["user_name"] == login_test_user["name"]
    assert updated_like["game_log_id"] == game_log_id
    assert updated_like["flag"] is False


@pytest.mark.asyncio
async def test_update_like_toggle_to_true(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test updating a like (toggling flag back to True)."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )  # Toggle to False
    response = await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )  # Toggle to True

    assert response.status_code == status.HTTP_200_OK
    updated_like = response.json()
    assert updated_like["flag"] is True


@pytest.mark.asyncio
async def test_update_like_does_not_exist(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test updating a like that doesn't exist (should suggest POST)."""
    game_log_id = 1
    access_token = login_test_user["access_token"]

    response = await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["message"] == "Like operation requested"
    assert content["action"] == "POST"
    assert (
        content["endpoint"]
        == f"/api/{settings.API_VERSION}/game_log_like/create/{game_log_id}"
    )


@pytest.mark.asyncio
async def test_update_like_non_existent_game_log(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test updating a like for a non-existent game log."""
    non_existent_game_log_id = 9999
    access_token = login_test_user["access_token"]

    response = await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{non_existent_game_log_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        "detail": f"Game log [{non_existent_game_log_id}] is not found."
    }


@pytest.mark.asyncio
async def test_update_like_no_auth(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test updating a like without authentication."""
    game_log_id = 1
    response = await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id}",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_delete_inactive_likes_success(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    login_admin_user: USER_DATA,
    db_session: AsyncSession,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test admin successfully deleting inactive likes."""
    game_log_id_inactive_like = 1  # Will be liked and unliked by login_test_user
    game_log_id_active_like = 3  # Will be liked by login_test_user and remain active

    user_token = login_test_user["access_token"]
    user_name = login_test_user["name"]
    admin_token = login_admin_user["access_token"]

    # Create and unlike for game_log_id_inactive_like
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_inactive_like}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    await async_client.patch(
        f"{GAME_LOG_LIKE_API_URL}/update/{game_log_id_inactive_like}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Create active like for game_log_id_active_like
    await async_client.post(
        f"{GAME_LOG_LIKE_API_URL}/create/{game_log_id_active_like}",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    # Admin deletes inactive likes
    delete_response = await async_client.delete(
        f"{GAME_LOG_LIKE_API_URL}/delete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT

    # Verify in DB
    inactive_like_db = await db_session.execute(
        select(GameLogLikeModel).where(
            GameLogLikeModel.game_log_id == game_log_id_inactive_like,
            GameLogLikeModel.user_name == user_name,
        )
    )
    assert inactive_like_db.scalars().first() is None

    active_like_db = await db_session.execute(
        select(GameLogLikeModel).where(
            GameLogLikeModel.game_log_id == game_log_id_active_like,
            GameLogLikeModel.user_name == user_name,
        )
    )
    fetched_active_like = active_like_db.scalars().first()
    assert fetched_active_like is not None
    assert fetched_active_like.flag is True


@pytest.mark.asyncio
async def test_delete_inactive_likes_none_to_delete(
    async_client: AsyncClient,
    login_admin_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test admin deleting when no inactive likes exist."""
    admin_token = login_admin_user["access_token"]
    response = await async_client.delete(
        f"{GAME_LOG_LIKE_API_URL}/delete",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_delete_inactive_likes_no_admin_auth(
    async_client: AsyncClient,
    login_test_user: USER_DATA,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test deleting inactive likes by a non-admin user."""
    user_token = login_test_user["access_token"]
    response = await async_client.delete(
        f"{GAME_LOG_LIKE_API_URL}/delete",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_delete_inactive_likes_no_auth_at_all(
    async_client: AsyncClient,
    create_test_all_game_log: Tuple[USER_DATA, GAME_LOG_DATA_LIST],
):
    """Test deleting inactive likes without any authentication."""
    response = await async_client.delete(
        f"{GAME_LOG_LIKE_API_URL}/delete",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
