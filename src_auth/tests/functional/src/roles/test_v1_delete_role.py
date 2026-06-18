from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.features.roles.v1.models import Role
from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_delete_role_success(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    create_payload = {
        "name": "DeleteMe",
        "description": "Role to be deleted",
    }
    create_body, _, _ = await make_request(
        "POST",
        "/v1/roles",
        data=create_payload,
        cookies=cookies,
    )
    role_id = create_body["id"]

    body, status, _ = await make_request(
        "DELETE",
        f"/v1/roles/{role_id}",
        cookies=cookies,
    )

    assert status == 200
    assert body == {"status": "success"}


async def test_delete_role_not_found(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    random_id = uuid4()

    body, status, _ = await make_request(
        "DELETE",
        f"/v1/roles/{random_id}",
        cookies=cookies,
    )

    assert status == 404
    assert body["detail"] == "Role not found"


async def test_delete_role_unauthorized(
    make_request: MakeRequestType,
    clear_roles: None,
) -> None:
    random_id = uuid4()

    body, status, _ = await make_request(
        "DELETE",
        f"/v1/roles/{random_id}",
        cookies={
            test_settings.access_cookie_name: None,
            test_settings.refresh_cookie_name: None,
        },
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_delete_role_forbidden(
    make_request: MakeRequestType,
    clear_roles: None,
    get_user_cookies: GetCookieType,
) -> None:
    cookies = await get_user_cookies(
        make_request,
        email="non-admin@example.com",
        password="Password123!",
    )
    random_id = uuid4()

    body, status, _ = await make_request(
        "DELETE",
        f"/v1/roles/{random_id}",
        cookies=cookies,
    )

    assert status == 403
    assert body["detail"] == "Access denied"


async def test_delete_system_role_forbidden(
    make_request: MakeRequestType,
    db_session: AsyncSession,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)

    query = select(Role).where(Role.name == test_settings.admin_role)
    result = await db_session.execute(query)
    system_role = result.scalar_one()

    body, status, _ = await make_request(
        "DELETE",
        f"/v1/roles/{system_role.id}",
        cookies=cookies,
    )

    assert status == 403
    assert body["detail"] == "Access denied"
