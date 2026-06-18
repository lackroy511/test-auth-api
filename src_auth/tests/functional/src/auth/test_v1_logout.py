from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_logout_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "logout-test@example.com",
        "first_name": "Logout",
        "last_name": "TestUser",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "logout-test@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    body, status, _ = await make_request(
        "POST",
        "/v1/logout",
        cookies=cookies,
    )
    assert status == 200


async def test_logout_unauthorized(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    body, status, _ = await make_request("POST", "/v1/logout")

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_logout_invalid_token(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    cookies = {test_settings.access_cookie_name: "invalid-token"}
    body, status, _ = await make_request("POST", "/v1/logout", cookies=cookies)

    assert status == 401
    assert body["detail"] == "Invalid or expired token"
