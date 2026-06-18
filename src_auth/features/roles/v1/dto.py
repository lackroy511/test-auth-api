from dataclasses import dataclass
from uuid import UUID


@dataclass
class CreateRoleDTO:
    name: str
    description: str | None = None


@dataclass
class RoleDTO:
    id: UUID
    name: str
    description: str | None = None
