from uuid import uuid4

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_revoke_role_success(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "revoke-success@example.com",
        "first_name": "Revoke",
        "last_name": "Success",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "TestRoleRevokeSuccess",
        "description": "Description for revoke success test",
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
    _, status, _ = await make_request("POST", assign_path, cookies=admin_cookies)
    assert status == 200

    revoke_path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("DELETE", revoke_path, cookies=admin_cookies)

    assert status == 200


async def test_revoke_role_not_found(
    make_request: MakeRequestType,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_id = str(uuid4())
    role_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("DELETE", path, cookies=admin_cookies)

    assert status == 404
    assert body["detail"] == "User or role not found"


async def test_revoke_role_unauthorized(
    make_request: MakeRequestType,
) -> None:
    user_id = str(uuid4())
    role_id = str(uuid4())
    path = f"/v1/roles/{role_id}/users/{user_id}"

    body, status, _ = await make_request(
        "DELETE",
        path,
        cookies={test_settings.access_cookie_name: None},
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_revoke_role_forbidden(
    make_request: MakeRequestType,
    clear_users_table: None,
    clear_roles: None,
    get_user_cookies: GetCookieType,
    get_admin_cookies: GetCookieType,
) -> None:
    admin_cookies = await get_admin_cookies(make_request)

    user_payload = {
        "email": "revoke-forbidden@example.com",
        "first_name": "Revoke",
        "last_name": "Forbidden",
        "password": "Password123!",
        "password_confirm": "Password123!",
    }
    user_body, status, _ = await make_request("POST", "/v1/register", data=user_payload)
    assert status == 200
    user_id = user_body["id"]

    role_payload = {
        "name": "TestRoleRevokeForbidden",
        "description": "Description for revoke forbidden test",
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

    user_cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )

    revoke_path = f"/v1/roles/{role_id}/users/{user_id}"
    body, status, _ = await make_request("DELETE", revoke_path, cookies=user_cookies)

    assert status == 403
    assert body["detail"] == "Access denied"
