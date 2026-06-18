import pytest

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_change_email_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "user1@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "user1@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {
        "email": "new-email@example.com",
        "current_password": "Password123!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-email",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["status"] == "success"


async def test_change_email_conflict(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    user1_payload = {
        "email": "user1@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=user1_payload)

    user2_payload = {
        "email": "user2@example.com",
        "first_name": "Jane",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=user2_payload)

    login_payload = {
        "email": "user1@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {"email": "user2@example.com", "current_password": "Password123!"}
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-email",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 409
    assert body["detail"] == "User already exists"


async def test_change_email_wrong_password(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "user1@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "user1@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {
        "email": "new-email@example.com",
        "current_password": "wrong-password",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-email",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 401
    assert body["detail"] == "Invalid credentials"


async def test_change_email_unauthorized(
    make_request: MakeRequestType,
) -> None:
    change_payload = {"email": "new-email@example.com"}
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-email",
        data=change_payload,
        cookies={test_settings.access_cookie_name: "invalid-token"},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {"email": "not-an-email", "current_password": "somepass"},
            "value is not a valid email address",
        ),
        ({}, "Field required"),
    ],
)
async def test_change_email_validation(
    make_request: MakeRequestType,
    payload: dict,
    expected_error: str,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)
    login_payload = {
        "email": "test@example.com",
        "password": "Password123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-email",
        data=payload,
        cookies=cookies,
    )

    assert status == 422
    errors = body.get("detail", [])
    if isinstance(errors, list):
        error_messages = [e.get("msg", "") for e in errors]
        assert any(expected_error in msg for msg in error_messages)
    else:
        assert expected_error in str(body["detail"])
