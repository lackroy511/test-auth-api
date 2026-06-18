from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.features.users.v1.models import User
from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_get_me_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "me-test@example.com",
        "first_name": "TestUser",
        "last_name": "TestUser",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "me-test@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    body, status, _ = await make_request(
        "GET",
        "/v1/users/me",
        cookies=cookies,
    )

    assert status == 200
    assert body["email"] == register_payload["email"]
    assert body["first_name"] == register_payload["first_name"]
    assert body["last_name"] == register_payload["last_name"]


async def test_get_me_unauthorized(
    make_request: MakeRequestType,
) -> None:
    body, status, _ = await make_request(
        "GET",
        "/v1/users/me",
        cookies={test_settings.access_cookie_name: "invalid-token"},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_get_me_invalid_token(
    make_request: MakeRequestType,
) -> None:
    body, status, _ = await make_request(
        "GET",
        "/v1/users/me",
        cookies={test_settings.access_cookie_name: "invalid-token"},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_get_me_not_found(
    make_request: MakeRequestType,
    db_session: AsyncSession,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "deleted-test@example.com",
        "first_name": "Deleted",
        "last_name": "User",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "deleted-test@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    query = delete(User).where(User.email == register_payload["email"])
    await db_session.execute(query)
    await db_session.commit()

    body, status, _ = await make_request("GET", "/v1/users/me", cookies=cookies)

    assert status == 404
    assert body["detail"] == "User not found"
