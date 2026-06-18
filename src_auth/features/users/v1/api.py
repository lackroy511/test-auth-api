from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src_auth.core.security.jwt import TokenPayload
from src_auth.features.shared.dependencies import get_current_user_payload
from src_auth.features.shared.schemas import ErrorResponse, StatusResponse, UserResponse
from src_auth.features.users.v1.schemas import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    UserAuthHistoryResponse,
)
from src_auth.features.users.v1.service import UserService, get_user_service

router = APIRouter(prefix="/v1", tags=["Users V1"])


@router.get(
    "/users/me",
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
async def get_current_user(
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> UserResponse:
    user = await user_service.get_user_by_id(UUID(token_payload.user_id))
    return UserResponse.model_validate(user)


@router.patch(
    "/users/me/change-email",
    responses={401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def change_email(
    request: ChangeEmailRequest,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> StatusResponse:
    await user_service.change_email(
        UUID(token_payload.user_id),
        request.email,
        request.current_password,
    )
    return StatusResponse(status="success")


@router.patch(
    "/users/me/change-password",
    responses={401: {"model": ErrorResponse}},
)
async def change_password(
    request: ChangePasswordRequest,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> StatusResponse:
    await user_service.change_password(
        UUID(token_payload.user_id),
        request.current_password,
        request.password,
    )
    return StatusResponse(status="success")


@router.get(
    "/users/me/auth-history",
    responses={401: {"model": ErrorResponse}},
)
async def get_auth_history(
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    user_service: Annotated[UserService, Depends(get_user_service)],
) -> list[UserAuthHistoryResponse]:
    history = await user_service.get_auth_history(UUID(token_payload.user_id))
    return [
        UserAuthHistoryResponse(user_agent=entry.user_agent, auth_at=entry.auth_at)
        for entry in history
    ]
