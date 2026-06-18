import pytest

from src_auth.tests.functional.conftest import MakeRequestType


async def test_register_success(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    body, status, _ = await make_request("POST", "/v1/register", data=payload)

    assert status == 200
    assert body["email"] == payload["email"]
    assert body["first_name"] == payload["first_name"]


async def test_register_conflict(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "duplicate@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    await make_request("POST", "/v1/register", data=payload)

    body, status, _ = await make_request("POST", "/v1/register", data=payload)

    assert status == 409
    assert body["detail"] == "User already exists"


async def test_register_optional_last_name(
    make_request: MakeRequestType,
    clear_users_table: None,
) -> None:
    payload = {
        "email": "no-lastname@example.com",
        "first_name": "John",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    body, status, _ = await make_request("POST", "/v1/register", data=payload)

    assert status == 200
    assert body["email"] == payload["email"]


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "DifferentPass!",
            },
            "Passwords do not match",
        ),
        (
            {
                "email": "not-an-email",
                "first_name": "John",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "value is not a valid email address",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "Jo",
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at least 3 characters",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "A" * 51,
                "last_name": "Doe",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Do",
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at least 3 characters",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "B" * 51,
                "password": "Password123!",
                "password_confirm": "Password123!",
            },
            "String should have at most 50 characters",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "123",
                "password_confirm": "123",
            },
            "String should have at least 8 characters",
        ),
        (
            {
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "password": "P" * 101,
                "password_confirm": "P" * 101,
            },
            "String should have at most 100 characters",
        ),
    ],
)
async def test_register_validation(
    make_request: MakeRequestType,
    clear_users_table: None,
    payload: dict,
    expected_error: str,
) -> None:
    body, status, _ = await make_request("POST", "/v1/register", data=payload)

    assert status == 422
    errors = body.get("detail", [])
    if isinstance(errors, list):
        error_messages = [e.get("msg", "") for e in errors]
        assert any(expected_error in msg for msg in error_messages)
    else:
        assert expected_error in str(body["detail"])
