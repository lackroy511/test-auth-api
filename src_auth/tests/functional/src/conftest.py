from typing import AsyncGenerator

from pytest_asyncio import fixture as async_fixture
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.features.roles.v1.models import Role, user_roles
from src_auth.features.users.v1.models import User, UserAuthHistory
from src_auth.tests.functional.settings import test_settings


@async_fixture
async def clear_users_table(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    async def clear() -> None:
        query = delete(User).where(User.email != test_settings.admin_email)
        await db_session.execute(query)
        await db_session.commit()

    yield
    await clear()


@async_fixture
async def clear_auth_history_table(
    db_session: AsyncSession,
) -> AsyncGenerator[None, None]:
    async def clear() -> None:
        query = delete(UserAuthHistory)
        await db_session.execute(query)
        await db_session.commit()

    yield
    await clear()


@async_fixture
async def clear_roles(db_session: AsyncSession) -> AsyncGenerator[None, None]:
    async def clear() -> None:
        admin_q = select(User).where(User.email == test_settings.admin_email)
        admin = await db_session.execute(admin_q)
        admin = admin.scalar_one()

        admin_role_q = select(Role).where(Role.name == test_settings.admin_role)
        admin_role = await db_session.execute(admin_role_q)
        admin_role = admin_role.scalar_one()

        clear_rel_query = delete(user_roles).where(
            user_roles.c.user_id != admin.id,
            user_roles.c.user_id != admin_role.id,
        )
        await db_session.execute(clear_rel_query)
        await db_session.commit()

        clear_roles_query = delete(Role).where(
            Role.name.not_in(test_settings.default_user_roles),
        )
        await db_session.execute(clear_roles_query)
        await db_session.commit()

    yield
    await clear()
