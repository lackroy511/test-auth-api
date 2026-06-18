from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CerateRoleRequest(BaseModel):
    name: str = Field(min_length=3, max_length=50)
    description: str | None = Field(None, min_length=3, max_length=200)


class UpdateRoleRequest(BaseModel):
    name: str | None = Field(None, min_length=3, max_length=50)
    description: str | None = Field(None, min_length=3, max_length=200)


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class IsRoleAssignedResponse(BaseModel):
    is_assigned: bool
