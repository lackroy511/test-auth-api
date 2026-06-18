import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src_auth.core.exc.exceptions import (
    AccessDeniedError,
    InvalidCredentialsError,
    InvalidTokenOrExpiredTokenError,
    RoleAlreadyAssignedError,
    RoleAlreadyExistsError,
    RoleNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserOrRoleNotFoundError,
)

log = logging.getLogger(__name__)


async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = request.headers.get("X-Request-Id")
    log.error("Unexpected error, request_id: %r", request_id, exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Unexpected server error",
            "request_id": request_id,
        },
    )


async def user_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "User already exists"})


async def user_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "User not found"})


async def invalid_credentials_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})


async def invalid_token_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})


async def role_not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Role not found"})


async def user_or_role_not_found_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "User or role not found"})


async def role_already_assigned_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Role already assigned"})


async def role_already_exists_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": "Role already exists"})


async def access_denied_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": "Access denied"})


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(Exception, unexpected_error_handler)
    app.add_exception_handler(UserAlreadyExistsError, user_already_exists_handler)
    app.add_exception_handler(UserNotFoundError, user_not_found_handler)
    app.add_exception_handler(InvalidCredentialsError, invalid_credentials_handler)
    app.add_exception_handler(InvalidTokenOrExpiredTokenError, invalid_token_handler)
    app.add_exception_handler(RoleNotFoundError, role_not_found_handler)
    app.add_exception_handler(UserOrRoleNotFoundError, user_or_role_not_found_handler)
    app.add_exception_handler(RoleAlreadyAssignedError, role_already_assigned_handler)
    app.add_exception_handler(RoleAlreadyExistsError, role_already_exists_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
