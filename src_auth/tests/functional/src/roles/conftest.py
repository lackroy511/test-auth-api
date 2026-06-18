from typing import Awaitable, Callable

from pytest_asyncio import fixture as async_fixture

from src_auth.tests.functional.conftest import MakeRequestType
from src_auth.tests.functional.settings import test_settings

GetCookieType = Callable[..., Awaitable[dict]]


@async_fixture
async def get_admin_cookies() -> GetCookieType:
    async def inner(make_request: MakeRequestType) -> dict:
        payload = {
            "email": test_settings.admin_email,
            "password": test_settings.admin_password,
        }
        _, _, cookies = await make_request("POST", "/v1/login", data=payload)
        return cookies

    return inner


@async_fixture
async def get_user_cookies() -> GetCookieType:
    async def inner(
        make_request: MakeRequestType,
        email: str,
        password: str,
    ) -> dict:
        register_payload = {
            "email": email,
            "first_name": "User",
            "last_name": "Test",
            "password": password,
            "password_confirm": password,
        }
        await make_request("POST", "/v1/register", data=register_payload)

        login_payload = {
            "email": email,
            "password": password,
        }
        _, _, cookies = await make_request("POST", "/v1/login", data=login_payload)
        return cookies

    return inner
