from uuid import uuid4

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_assign_role_success(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "assign-success@example.com",
        "first_name": "Assign",
        "last_name": "Success",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "TestRoleSuccess",
        "description": "Description for success test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("POST", path, cookies=admin_cookies)

    assert status == 200


async def test_assign_role_not_found_user(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    role_payload = {
        "name": "TestRoleNotFoundUser",
        "description": "Description for not found user test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    user_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("POST", path, cookies=admin_cookies)

    assert status == 404
    assert body["detail"] == "User or role not found"


async def test_assign_role_not_found_role(
    make_request: MakeRequestType,
    clear_users_table: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "assign-nf-role@example.com",
        "first_name": "Assign",
        "last_name": "NF Role",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("POST", path, cookies=admin_cookies)

    assert status == 404
    assert body["detail"] == "User or role not found"


async def test_assign_role_conflict(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "assign-conflict@example.com",
        "first_name": "Assign",
        "last_name": "Conflict",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "TestRoleConflict",
        "description": "Description for conflict test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    path = f"/v1/roles/{role_id}/users/{user_id}"
    await make_request("POST", path, cookies=admin_cookies)

    body, status, _ = await make_request("POST", path, cookies=admin_cookies)

    assert status == 409
    assert body["detail"] == "Role already assigned"


async def test_assign_role_unauthorized(
    make_request: MakeRequestType,
) -> None:
    role_id = str(uuid4())
    user_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"

    body, status, _ = await make_request(
        "POST",
        path,
        cookies={test_settings.access_cookie_name: None},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_assign_role_forbidden(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_user_cookies: GetCookieType,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "assign-forbidden@example.com",
        "first_name": "Assign",
        "last_name": "Forbidden",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "TestRoleForbidden",
        "description": "Description for forbidden test",
    }
    role_body, status, _ = await make_request(
        "POST",
        "/v1/roles",
        data=role_payload,
        cookies=admin_cookies,
    )
    assert status == 200
    role_id = role_body["id"]

    user_cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )

    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("POST", path, cookies=user_cookies)

    assert status == 403
    assert body["detail"] == "Access denied"
