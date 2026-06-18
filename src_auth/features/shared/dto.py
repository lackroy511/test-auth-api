from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserDTO:
    id: UUID
    email: str
    first_name: str | None
    last_name: str | None
    password_hash: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
