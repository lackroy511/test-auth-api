from uuid import uuid4

from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src_auth.core.config.settings import settings
from src_auth.core.security.hash_pass import hash_password
from src_auth.features.roles.v1.models import Role, user_roles
from src_auth.features.users.v1.models import User


async def init_db(session: AsyncSession) -> None:
    await create_user_roles(session)
    await create_admin_user(session)


async def create_user_roles(session: AsyncSession) -> None:
    result = await session.execute(select(Role.name))
    existing_roles = set(result.scalars().all())

    missing_roles = [
        role for role in settings.default_user_roles if role not in existing_roles
    ]

    if not missing_roles:
        return

    for role in missing_roles:
        new_role = Role(name=role, description="Default role", is_system=True)
        session.add(new_role)

    await session.flush()


async def create_admin_user(session: AsyncSession) -> None:
    if len(settings.admin_password) < 12:
        raise ValueError("Admin password must be at least 12 characters long")

    query = select(Role).where(Role.name == settings.admin_role)
    result = await session.execute(query)
    admin_role = result.scalar_one_or_none()
    if not admin_role:
        raise ValueError("Admin role not found")

    query = select(User).where(User.email == settings.admin_email)
    result = await session.execute(query)
    admin_user = result.scalar_one_or_none()
    if not admin_user:
        admin_user = User(
            id=uuid4(),
            email=settings.admin_email,
            first_name="Admin",
            password_hash=hash_password(settings.admin_password),
            is_active=True,
        )
        session.add(admin_user)
        await session.flush()

    try:
        query = insert(user_roles).values(
            user_id=admin_user.id,
            role_id=admin_role.id,
        )
        await session.execute(query)
    except IntegrityError as e:
        if getattr(e.orig, "pgcode", None) == "23505":
            return
