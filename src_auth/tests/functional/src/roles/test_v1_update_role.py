from uuid import uuid4

import pytest

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_update_role_success(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    create_payload = {
        "name": "InitialRole",
        "description": "Initial description",
    }
    create_body, _, _ = await make_request(
        "POST",
        "/v1/roles",
        data=create_payload,
        cookies=cookies,
    )
    role_id = create_body["id"]

    update_payload = {
        "name": "UpdatedRole",
        "description": "Updated description",
    }
    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{role_id}",
        data=update_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["name"] == update_payload["name"].lower()
    assert body["description"] == update_payload["description"]


async def test_update_role_partial_name(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    create_payload = {
        "name": "InitialRole",
        "description": "Keep this description",
    }
    create_body, _, _ = await make_request(
        "POST",
        "/v1/roles",
        data=create_payload,
        cookies=cookies,
    )
    role_id = create_body["id"]

    update_payload = {
        "name": "NewName",
    }
    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{role_id}",
        data=update_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["name"] == update_payload["name"].lower()
    assert body["description"] == create_payload["description"]


async def test_update_role_partial_description(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    create_payload = {
        "name": "KeepThisName",
        "description": "Initial description",
    }
    create_body, _, _ = await make_request(
        "POST",
        "/v1/roles",
        data=create_payload,
        cookies=cookies,
    )
    role_id = create_body["id"]

    update_payload = {
        "description": "New description",
    }
    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{role_id}",
        data=update_payload,
        cookies=cookies,
    )

    assert status == 200
    assert body["name"] == create_payload["name"].lower()
    assert body["description"] == update_payload["description"]


async def test_update_role_unauthorized(
    make_request: MakeRequestType,
    clear_roles: None,
) -> None:
    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{uuid4()}",
        data={"name": "NewName"},
        cookies={
            test_settings.access_cookie_name: None,
            test_settings.refresh_cookie_name: None,
        },
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_update_role_forbidden(
    make_request: MakeRequestType,
    clear_roles: None,
    get_user_cookies: GetCookieType,
) -> None:
    cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )

    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{uuid4()}",
        data={"name": "NewName"},
        cookies=cookies,
    )

    assert status == 403
    assert body["detail"] == "Access denied"


async def test_update_role_not_found(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{uuid4()}",
        data={"name": "NewName"},
        cookies=cookies,
    )

    assert status == 404
    assert body["detail"] == "Role not found"


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
async def test_update_role_validation(
    make_request: MakeRequestType,
    clear_roles: None,
    payload: dict,
    expected_error: str,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    create_payload = {"name": "ValidRole", "description": "Valid description"}
    create_body, _, _ = await make_request(
        "POST",
        "/v1/roles",
        data=create_payload,
        cookies=cookies,
    )
    role_id = create_body["id"]

    body, status, _ = await make_request(
        "PATCH",
        f"/v1/roles/{role_id}",
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
