import pytest

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings


async def test_change_password_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "change-pass-test@example.com",
        "first_name": "Change",
        "last_name": "Password",
        "password": "OldPassword123!",
        "password_confirm": "OldPassword123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "change-pass-test@example.com",
        "password": "OldPassword123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {
        "current_password": "OldPassword123!",
        "password": "NewPassword456!",
        "password_confirm": "NewPassword456!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["status"] == "success"

    login_new_payload = {
        "email": "change-pass-test@example.com",
        "password": "NewPassword456!",
    }
    body, status, _ = await make_request("POST", "/v1/login", data=login_new_payload)
    assert status == 200

    login_old_payload = {
        "email": "change-pass-test@example.com",
        "password": "OldPassword123!",
    }
    body, status, _ = await make_request("POST", "/v1/login", data=login_old_payload)
    assert status == 401


async def test_change_password_unauthorized(
    make_request: MakeRequestType,
) -> None:
    change_payload = {
        "password": "NewPassword456!",
        "password_confirm": "NewPassword456!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=change_payload,
        cookies={test_settings.access_cookie_name: "invalid-token"},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {
                "current_password": "Password123!",
                "password": "NewPassword456!",
                "password_confirm": "DifferentPass789!",
            },
            "Passwords do not match",
        ),
        (
            {
                "password": "NewPassword456!",
                "password_confirm": "NewPassword456!",
            },
            "Field required",
        ),
    ],
)
async def test_change_password_validation(
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
        "/v1/users/me/change-password",
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


async def test_change_password_wrong_current_password(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    register_payload = {
        "email": "wrong-current@example.com",
        "first_name": "Wrong",
        "last_name": "Current",
        "password": "ActualPassword123!",
        "password_confirm": "ActualPassword123!",
    }
    await make_request("POST", "/v1/register", data=register_payload)

    login_payload = {
        "email": "wrong-current@example.com",
        "password": "ActualPassword123!",
    }
    _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)

    change_payload = {
        "current_password": "WrongPassword456!",
        "password": "NewPassword789!",
        "password_confirm": "NewPassword789!",
    }
    body, status, _ = await make_request(
        "PATCH",
        "/v1/users/me/change-password",
        data=change_payload,
        cookies=cookies,
    )

    assert status == 401
    assert body["detail"] == "Invalid credentials"

    login_old_payload = {
        "email": "wrong-current@example.com",
        "password": "ActualPassword123!",
    }
    body, status, _ = await make_request("POST", "/v1/login", data=login_old_payload)
    assert status == 200
