from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    first_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    last_name: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        server_default="false",
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"


class UserAuthHistory(Base):
    __tablename__ = "user_auth_history"

    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
    )
    user_agent: Mapped[str] = mapped_column(
        Text,
    )
    auth_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<AuthHistory {self.user_id} {self.user_agent} {self.auth_at}>"
