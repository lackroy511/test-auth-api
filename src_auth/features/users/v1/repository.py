from abc import ABC, abstractmethod
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.db.sql_alch import get_db_session
from src_auth.core.exc.exceptions import UserAlreadyExistsError
from src_auth.features.shared.dto import UserDTO
from src_auth.features.users.v1.dto import CreateUserDTO, UserAuthHistoryDTO
from src_auth.features.users.v1.models import User, UserAuthHistory


class UserRepoInterface(ABC):
    @abstractmethod
    async def create(self, user: CreateUserDTO) -> UserDTO:
        pass

    @abstractmethod
    async def get_by_id(self, id: UUID) -> UserDTO | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> UserDTO | None:
        pass

    @abstractmethod
    async def get_or_create(self, user: CreateUserDTO) -> UserDTO:
        pass

    @abstractmethod
    async def create_auth_entry(self, user_id: UUID, user_agent: str) -> None:
        pass

    @abstractmethod
    async def get_auth_history(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[UserAuthHistoryDTO]:
        pass

    @abstractmethod
    async def update_email(self, user_id: UUID, new_email: str) -> None:
        pass

    @abstractmethod
    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        pass


class UserRepo(UserRepoInterface):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, user: CreateUserDTO) -> UserDTO:
        try:
            return await self.create(user)
        except UserAlreadyExistsError:
            query = select(User).where(User.email == user.email)
            result = await self.session.execute(query)
            existing = result.scalar_one()
            return self._transform_user_to_dto(existing)

    async def create(self, user: CreateUserDTO) -> UserDTO:
        query = (
            insert(User)
            .values(
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                password_hash=user.password_hash,
                is_active=user.is_active,
            )
            .returning(User)
        )
        try:
            result = await self.session.execute(query)
        except IntegrityError as e:
            if getattr(e.orig, "pgcode", None) == "23505":
                raise UserAlreadyExistsError() from None

            raise

        created = result.scalar_one()
        return self._transform_user_to_dto(created)

    async def get_by_id(self, id: UUID) -> UserDTO | None:
        query = select(User).where(User.id == id)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._transform_user_to_dto(user)

    async def get_by_email(self, email: str) -> UserDTO | None:
        query = select(User).where(
            User.email == email,
            User.is_active.is_(True),
        )
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            return None

        return self._transform_user_to_dto(user)

    async def create_auth_entry(self, user_id: UUID, user_agent: str) -> None:
        query = insert(UserAuthHistory).values(user_id=user_id, user_agent=user_agent)
        await self.session.execute(query)

    async def get_auth_history(
        self,
        user_id: UUID,
        limit: int = 10,
    ) -> list[UserAuthHistoryDTO]:
        query = (
            select(UserAuthHistory)
            .where(UserAuthHistory.user_id == user_id)
            .order_by(UserAuthHistory.auth_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        history = result.scalars().all()
        return [
            UserAuthHistoryDTO(
                user_id=h.user_id,
                user_agent=h.user_agent,
                auth_at=h.auth_at,
            )
            for h in history
        ]

    async def update_email(self, user_id: UUID, new_email: str) -> None:
        query = update(User).where(User.id == user_id).values(email=new_email)
        try:
            await self.session.execute(query)
        except IntegrityError as e:
            if getattr(e.orig, "pgcode", None) == "23505":
                raise UserAlreadyExistsError() from None
            raise

    async def update_password(self, user_id: UUID, new_password_hash: str) -> None:
        query = (
            update(User)
            .where(User.id == user_id)
            .values(password_hash=new_password_hash)
        )
        await self.session.execute(query)

    def _transform_user_to_dto(self, user: User) -> UserDTO:
        return UserDTO(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            password_hash=user.password_hash,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


async def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepoInterface:
    return UserRepo(session=session)
