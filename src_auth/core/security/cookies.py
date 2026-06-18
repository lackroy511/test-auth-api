from fastapi import Response

from src_auth.core.config.settings import settings


def set_token_cookie(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=settings.access_token_ttl,
    )

    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        max_age=settings.refresh_token_ttl,
    )


def clear_token_cookie(response: Response) -> None:
    response.delete_cookie(key=settings.access_cookie_name)
    response.delete_cookie(key=settings.refresh_cookie_name)
