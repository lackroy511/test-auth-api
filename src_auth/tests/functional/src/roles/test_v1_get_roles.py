from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings
from src_auth.tests.functional.src.roles.conftest import GetCookieType


async def test_get_roles_success(
    make_request: MakeRequestType,
    clear_roles: None,
    get_admin_cookies: GetCookieType,
) -> None:
    cookies = await get_admin_cookies(make_request)
    body, status, _ = await make_request(
        "GET",
        "/v1/roles",
        cookies=cookies,
    )

    assert status == 200
    assert isinstance(body, list)


async def test_get_roles_unauthorized(
    make_request: MakeRequestType,
    clear_roles: None,
) -> None:
    body, status, _ = await make_request(
        "GET",
        "/v1/roles",
        cookies={
            test_settings.access_cookie_name: None,
            test_settings.refresh_cookie_name: None,
        },
    )

    assert status == 401
    assert body["detail"] == "Invalid or expired token"


async def test_get_roles_forbidden(
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
        "GET",
        "/v1/roles",
        cookies=cookies,
    )

    assert status == 403
    assert body["detail"] == "Access denied"
