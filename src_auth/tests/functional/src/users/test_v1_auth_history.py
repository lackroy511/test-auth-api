from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_get_auth_history_success(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_auth_history_table: None,
) -> None:
    register_payload = {
        "email": "history-test@example.com",
        "first_name": "History",
        "last_name": "TestUser",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "history-test@example.com",
        "password": "Password123!",
    }
    await make_request("POST", "/v1/login", data=login_payload)
    await make_request("POST", "/v1/login", data=login_payload)
    _, status, cookies = await make_request("POST", "/v1/login", data=login_payload)
    assert status == 200

    body, status, _ = await make_request(
        "GET",
        "/v1/users/me/auth-history",
        cookies=cookies,
    )
    assert status == 200
    assert isinstance(body, list)
    assert len(body) == 3
    assert "user_agent" in body[0]
    assert "auth_at" in body[0]


async def test_get_auth_history_unauthorized(
    make_request: MakeRequestType,
) -> None:
    body, status, _ = await make_request(
        "GET",
        "/v1/users/me/auth-history",
        cookies={
            test_settings.access_cookie_name: None,
            test_settings.refresh_cookie_name: None,
        },
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"
