import pytest

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_refresh_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "refresh-success@example.com",
        "first_name": "Refresh",
        "last_name": "Success",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "refresh-success@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    body, status, new_cookies = await make_request(
        "POST",
        "/v1/refresh",
        cookies=cookies,
    )

    assert status == 200
    assert test_settings.access_cookie_name in new_cookies
    assert test_settings.refresh_cookie_name in new_cookies


@pytest.mark.parametrize(
    "cookies, expected_detail",
    [
        ({test_settings.refresh_cookie_name: None}, "Invalid or expired token"),
        (
            {test_settings.refresh_cookie_name: "invalid-token-string"},
            "Invalid or expired token",
        ),
    ],
)
async def test_refresh_invalid_token(
    make_request: MakeRequestType,
    cookies: dict | None,
    expected_detail: str,
) -> None:
    body, status, _ = await make_request("POST", "/v1/refresh", cookies=cookies)

    assert status == 401
    assert body["detail"] == expected_detail


async def test_refresh_blacklisted_token(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "blacklist-test@example.com",
        "first_name": "Blacklist",
        "last_name": "Test",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "blacklist-test@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    await make_request("POST", "/v1/logout", cookies=cookies)

    body, status, _ = await make_request(
        "POST",
        "/v1/refresh",
        cookies=cookies,
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_refresh_revoked_session(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "revoke-test@example.com",
        "first_name": "Revoke",
        "last_name": "Test",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "revoke-test@example.com",
        "password": "Password123!",
    }
    _, _, old_cookies = await make_request("POST", "/v1/login", data=login_payload)
    _, _, new_cookies = await make_request("POST", "/v1/login", data=login_payload)

    await make_request("POST", "/v1/logout-all", cookies=new_cookies)

    body, status, _ = await make_request(
        "POST",
        "/v1/refresh",
        cookies=old_cookies,
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"
