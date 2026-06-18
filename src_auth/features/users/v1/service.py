from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src_auth.core.exc.exceptions import InvalidCredentialsError, UserNotFoundError
from src_auth.core.security.hash_pass import hash_password, verify_password
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.dto import CreateUserDTO, UserAuthHistoryDTO
from src_auth.features.users.v1.repository import (
    UserRepoInterface,
    get_user_repository,
)


class UserService:
    def __init__(self, repository: UserRepoInterface) -> None:
        self.repository = repository

    async def create_user(
        self,
        email: str,
        first_name: str | None,
        last_name: str | None,
        password: str | None,
    ) -> UserDTO:
        to_create = CreateUserDTO(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(password) if password else None,
        )
        return await self.repository.create(to_create)

    async def get_or_create_user(
        self,
        email: str,
        first_name: str | None,
        last_name: str | None,
        password: str | None,
    ) -> UserDTO:
        to_create = CreateUserDTO(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hash_password(password) if password else None,
        )
        return await self.repository.get_or_create(to_create)

    async def get_user_by_id(self, user_id: UUID) -> UserDTO:
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundError("User not found")

        return user

    async def get_user_by_email(self, email: str) -> UserDTO:
        user = await self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundError("User not found")

        return user

    async def create_auth_entry(self, user_id: UUID, user_agent: str) -> None:
        await self.repository.create_auth_entry(user_id, user_agent)

    async def get_auth_history(self, user_id: UUID) -> list[UserAuthHistoryDTO]:
        return await self.repository.get_auth_history(user_id)

    async def change_email(
        self,
        user_id: UUID,
        new_email: str,
        current_password: str,
    ) -> None:
        user = await self.get_user_by_id(user_id)
        if user.password_hash is not None:
            if not verify_password(current_password, user.password_hash):
                raise InvalidCredentialsError("Invalid credentials")
        else:
            raise InvalidCredentialsError("Invalid credentials")
        await self.repository.update_email(user_id, new_email)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self.get_user_by_id(user_id)
        if user.password_hash is None:
            raise InvalidCredentialsError("Invalid credentials")
        if not verify_password(current_password, user.password_hash):
            raise InvalidCredentialsError("Invalid credentials")
        hashed_password = hash_password(new_password)
        await self.repository.update_password(user_id, hashed_password)


async def get_user_service(
    user_repository: Annotated[UserRepoInterface, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository=user_repository)
