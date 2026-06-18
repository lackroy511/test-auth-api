from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from src_auth.core.config.settings import settings
from src_auth.core.security.cookies import clear_token_cookie, set_token_cookie
from src_auth.features.auth.v1.schemas import (
    LoginRequest,
    RegisterRequest,
)
from src_auth.features.auth.v1.service import (
    AuthService,
    get_auth_service,
)
from src_auth.features.shared.dependencies import (
    get_access_token,
    get_refresh_token,
)
from src_auth.features.shared.schemas import ErrorResponse, StatusResponse, UserResponse

router = APIRouter(prefix="/v1", tags=["Auth V1"])


@router.post(
    "/register",
    responses={409: {"model": ErrorResponse}},
)
async def register(
    user_data: RegisterRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> UserResponse:
    new_user = await auth_service.register_user(
        email=user_data.email,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        password=user_data.password,
    )
    return UserResponse.model_validate(new_user)


@router.post(
    "/login",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def login(
    request: Request,
    login_data: LoginRequest,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    response: Response,
) -> UserResponse:
    user_agent = request.headers.get("user-agent", "Unknown user-agent")
    logged_user, access, refresh = await auth_service.login_user(
        email=login_data.email,
        password=login_data.password,
        user_agent=user_agent,
    )
    set_token_cookie(response, access, refresh)
    return UserResponse.model_validate(logged_user)


@router.post(
    "/refresh",
    responses={401: {"model": ErrorResponse}},
)
async def refresh(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> StatusResponse:
    access = request.cookies.get(settings.access_cookie_name)
    refresh = request.cookies.get(settings.refresh_cookie_name)
    new_access, new_refresh = await auth_service.refresh_tokens(access, refresh)
    set_token_cookie(response, new_access, new_refresh)
    return StatusResponse()


@router.post(
    "/logout",
    responses={401: {"model": ErrorResponse}},
)
async def logout(
    access_token: Annotated[str | None, Depends(get_access_token)],
    refresh_token: Annotated[str | None, Depends(get_refresh_token)],
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> StatusResponse:
    await auth_service.logout_user(access_token, refresh_token)
    clear_token_cookie(response)
    return StatusResponse()


@router.post(
    "/logout-all",
    responses={401: {"model": ErrorResponse}},
)
async def logout_all(
    access_token: Annotated[str | None, Depends(get_access_token)],
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> StatusResponse:
    await auth_service.logout_all_user_sessions(access_token)
    clear_token_cookie(response)
    return StatusResponse()
