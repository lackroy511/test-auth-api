from src_auth.tests.functional.conftest import MakeRequestType


async def test_logout_all_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "logout-all-test@example.com",
        "first_name": "Logout",
        "last_name": "AllUser",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "logout-all-test@example.com",
        "password": "Password123!",
    }
    _, _, cookies_1 = await make_request("POST", "/v1/login", data=login_payload)
    _, _, cookies_2 = await make_request("POST", "/v1/login", data=login_payload)
    _, _, cookies_3 = await make_request("POST", "/v1/login", data=login_payload)

    _, status, _ = await make_request(
        "POST",
        "/v1/logout-all",
        cookies=cookies_3,
    )
    assert status == 200

    _, status_1, _ = await make_request("POST", "/v1/refresh", cookies=cookies_1)
    _, status_2, _ = await make_request("POST", "/v1/refresh", cookies=cookies_2)
    _, status_3, _ = await make_request("POST", "/v1/refresh", cookies=cookies_3)

    assert status_1 == 401
    assert status_2 == 401
    assert status_3 == 401


async def test_logout_all_unauthorized(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    body, status, _ = await make_request("POST", "/v1/logout-all")

    assert status == 401
    assert body["detail"] == "Invalid or expired token"
