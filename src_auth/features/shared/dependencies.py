from typing import Annotated

from fastapi import Depends
from fastapi.security import APIKeyCookie

from src_auth.core.config.settings import RolesType, settings
from src_auth.core.exc.exceptions import (
    AccessDeniedError,
    InvalidTokenOrExpiredTokenError,
)
from src_auth.core.security.jwt import TokenPayload
from src_auth.features.auth.v1.service import SessionService, get_session_service

access_cookie_scheme = APIKeyCookie(
    name=settings.access_cookie_name,
    auto_error=False,
)
refresh_cookie_scheme = APIKeyCookie(
    name=settings.refresh_cookie_name,
    auto_error=False,
)


class RequireRole:
    def __init__(self, allowed_roles: list[RolesType]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(
        self,
        token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    ) -> None:
        user_roles = getattr(token_payload, "user_roles", [])

        has_access = bool(set(user_roles) & set(self.allowed_roles))
        if not has_access:
            raise AccessDeniedError("Access denied")


async def get_current_user_payload(
    access_token: Annotated[str | None, Depends(access_cookie_scheme)],
    session_service: Annotated[
        SessionService,
        Depends(get_session_service),
    ],
) -> TokenPayload:
    if not access_token:
        raise InvalidTokenOrExpiredTokenError("Access token not found")

    payload = session_service.decode_token(access_token, "access")
    await session_service.verify_session(payload, access_token)
    return payload


async def get_access_token(
    access_token: Annotated[str | None, Depends(access_cookie_scheme)],
) -> str | None:
    return access_token


async def get_refresh_token(
    refresh_token: Annotated[str | None, Depends(refresh_cookie_scheme)],
) -> str | None:
    return refresh_token
