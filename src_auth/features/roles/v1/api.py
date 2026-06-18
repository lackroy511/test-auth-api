from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src_auth.core.config.settings import settings
from src_auth.core.security.jwt import TokenPayload
from src_auth.features.roles.v1.schemas import (
    CerateRoleRequest,
    IsRoleAssignedResponse,
    RoleResponse,
    UpdateRoleRequest,
)
from src_auth.features.roles.v1.service import RoleService, get_role_service
from src_auth.features.shared.dependencies import RequireRole, get_current_user_payload
from src_auth.features.shared.schemas import ErrorResponse, StatusResponse

router = APIRouter(
    prefix="/v1",
    tags=["Roles V1"],
    dependencies=[Depends(RequireRole(allowed_roles=[settings.admin_role]))],
)


@router.post(
    "/roles",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def create_role(
    role_data: CerateRoleRequest,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleResponse:
    role = await role_service.create_role(
        name=role_data.name,
        description=role_data.description,
    )
    return RoleResponse.model_validate(role)


@router.get(
    "/roles",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def get_roles(
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> list[RoleResponse]:
    roles = await role_service.get_all_roles()
    return [RoleResponse.model_validate(role) for role in roles]


@router.patch(
    "/roles/{role_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def update_role(
    role_id: UUID,
    update_data: UpdateRoleRequest,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> RoleResponse:
    role = await role_service.update_role(
        role_id=role_id,
        name=update_data.name,
        description=update_data.description,
    )
    return RoleResponse.model_validate(role)


@router.delete(
    "/roles/{role_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def delete_role(
    role_id: UUID,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> StatusResponse:
    await role_service.delete_role(role_id=role_id)
    return StatusResponse()


@router.post(
    "/roles/{role_id}/users/{user_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
    },
)
async def assign_role(
    role_id: UUID,
    user_id: UUID,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> StatusResponse:
    await role_service.assign_user_to_role(
        user_id=user_id,
        role_id=role_id,
    )
    return StatusResponse()


@router.get(
    "/roles/{role_id}/users/{user_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
    },
)
async def check_role_assignment(
    role_id: UUID,
    user_id: UUID,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> IsRoleAssignedResponse:
    is_assigned = await role_service.is_user_assigned_to_role(
        user_id=user_id,
        role_id=role_id,
    )
    return IsRoleAssignedResponse(is_assigned=is_assigned)


@router.delete(
    "/roles/{role_id}/users/{user_id}",
    responses={
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
)
async def revoke_role(
    role_id: UUID,
    user_id: UUID,
    token_payload: Annotated[TokenPayload, Depends(get_current_user_payload)],
    role_service: Annotated[RoleService, Depends(get_role_service)],
) -> StatusResponse:
    await role_service.revoke_user_from_role(
        user_id=user_id,
        role_id=role_id,
    )
    return StatusResponse()
