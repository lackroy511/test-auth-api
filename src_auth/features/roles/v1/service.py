from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src_auth.core.exc.exceptions import (
    AccessDeniedError,
    RoleNotFoundError,
    UserOrRoleNotFoundError,
)
from src_auth.features.roles.v1.dto import CreateRoleDTO, RoleDTO
from src_auth.features.roles.v1.repository import (
    RoleRepositoryInterface,
    get_role_repository,
)


class RoleService:
    def __init__(self, repository: RoleRepositoryInterface) -> None:
        self.repository = repository

    async def create_role(
        self,
        name: str,
        description: str | None,
    ) -> RoleDTO:
        role_dto = CreateRoleDTO(
            name=name.lower(),
            description=description,
        )
        return await self.repository.create_role(role=role_dto)

    async def get_all_roles(
        self,
    ) -> list[RoleDTO]:
        return await self.repository.get_all_roles()

    async def get_all_user_roles(
        self,
        user_id: UUID,
    ) -> list[RoleDTO]:
        return await self.repository.get_all_user_roles(user_id=user_id)

    async def update_role(
        self,
        role_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> RoleDTO:
        if await self.repository.is_system_role(role_id=role_id):
            raise AccessDeniedError("Cannot update a system role")

        updated = await self.repository.update_role(
            role_id=role_id,
            name=name.lower() if name else None,
            description=description,
        )
        if not updated:
            raise RoleNotFoundError("Role not found")

        return updated

    async def delete_role(
        self,
        role_id: UUID,
    ) -> bool:
        if await self.repository.is_system_role(role_id=role_id):
            raise AccessDeniedError("Cannot delete system role")

        is_deleted = await self.repository.delete_role(role_id=role_id)
        if not is_deleted:
            raise RoleNotFoundError("Role not found")

        return is_deleted

    async def assign_user_to_role(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> None:
        await self.repository.assign_user_to_role(
            user_id=user_id,
            role_id=role_id,
        )

    async def is_user_assigned_to_role(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> bool:
        return await self.repository.is_user_assigned_to_role(
            user_id=user_id,
            role_id=role_id,
        )

    async def revoke_user_from_role(
        self,
        user_id: UUID,
        role_id: UUID,
    ) -> None:
        is_revoked = await self.repository.revoke_user_from_role(
            user_id=user_id,
            role_id=role_id,
        )
        if not is_revoked:
            raise UserOrRoleNotFoundError("User or role not found")


async def get_role_service(
    role_repo: Annotated[RoleRepositoryInterface, Depends(get_role_repository)],
) -> RoleService:
    return RoleService(role_repo)
