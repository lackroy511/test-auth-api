import pytest

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_create_role_success(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    payload = {
        "name": "Manager",
        "description": "Role for managers",
    }
    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["name"] == payload["name"].lower()
    assert body["description"] == payload["description"]
    assert "id" in body


async def test_create_role_no_description(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    payload = {
        "name": "Editor",
    }
    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["name"] == payload["name"].lower()
    assert body["description"] is None


async def test_create_role_conflict(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    payload = {
        "name": "DuplicateRole",
        "description": "Description",
    }
    await make_request("POST", "/v1/roles", data=payload, cookies=cookies)

    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=payload,
        cookies=cookies,
    )

    assert status == 409
    assert body["detail"] == "Role already exists"


async def test_create_role_unauthorized(
    make_request: MakeRequestType,
    clear_roles: None,
) -> None:
    payload = {
        "name": "UnauthorizedRole",
        "description": "Description",
    }
    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=payload,
        cookies={
            test_settings.access_cookie_name: None,
            test_settings.refresh_cookie_name: None,
        },
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_create_role_forbidden(
    make_request: MakeRequestType,
    clear_roles: None,
    get_user_cookies: GetCookieType,
) -> None:
    cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )
    payload = {
        "name": "ForbiddenRole",
        "description": "Description",
    }
    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=payload,
        cookies=cookies,
    )

    assert status == 403
    assert body["detail"] == "Access denied"


@pytest.mark.parametrize(
    "payload, expected_error",
    [
        (
            {"name": "sh", "description": "Valid desc"},
            "String should have at least 3 characters",
        ),
        (
            {"name": "a" * 51, "description": "Valid desc"},
            "String should have at most 50 characters",
        ),
        (
            {"name": "ValidName", "description": "sh"},
            "String should have at least 3 characters",
        ),
        (
            {"name": "ValidName", "description": "b" * 201},
            "String should have at most 200 characters",
        ),
    ],
)
async def test_create_role_validation(
    make_request: MakeRequestType,
    clear_roles: None,
    payload: dict,
    expected_error: str,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    body, status, _ = await make_request(
        "POST",
        "/v1/roles",
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
