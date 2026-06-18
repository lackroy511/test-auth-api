from uuid import UUID

from sqlalchemy import ForeignKey, Integer, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from src_auth.core.db.sql_alch import Base


class TokenVersion(Base):
    __tablename__ = "token_versions"
    user_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        unique=True,
    )
    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    def __repr__(self) -> str:
        return f"TokenVersion(user_id={self.user_id}, version={self.version})"

