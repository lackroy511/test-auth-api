from dataclasses import dataclass
from uuid import UUID


@dataclass
class TokenVersionDTO:
    user_id: UUID
    version: int
