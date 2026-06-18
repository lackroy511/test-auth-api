from uuid import uuid4

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_check_role_assigned_success(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "check-assigned@example.com",
        "first_name": "Check",
        "last_name": "Assigned",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "CheckRoleAssigned",
        "description": "Description for assigned check test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    assign_path = f"/v1/roles/{role_id}/users/{user_id}"
    await make_request("POST", assign_path, cookies=admin_cookies)

    check_path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("GET", check_path, cookies=admin_cookies)

    assert status == 200
    assert body["is_assigned"] is True


async def test_check_role_not_assigned_success(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "check-not-assigned@example.com",
        "first_name": "Check",
        "last_name": "NotAssigned",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "CheckRoleNotAssigned",
        "description": "Description for not assigned check test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    check_path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("GET", check_path, cookies=admin_cookies)

    assert status == 200
    assert body["is_assigned"] is False


async def test_check_role_unauthorized(
    make_request: MakeRequestType,
) -> None:
    role_id = str(uuid4())
    user_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"

    body, status, _ = await make_request(
        "GET",
        path,
        cookies={test_settings.access_cookie_name: None},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_check_role_forbidden(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_user_cookies: GetCookieType,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    role_payload = {
        "name": "CheckRoleForbidden",
        "description": "Description for forbidden check test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    user_payload = {
        "email": "check-forbidden@example.com",
        "first_name": "Check",
        "last_name": "Forbidden",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    user_cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )

    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("GET", path, cookies=user_cookies)

    assert status == 403
    assert body["detail"] == "Access denied"
