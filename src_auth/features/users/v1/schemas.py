from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator


class ChangeEmailRequest(BaseModel):
    email: EmailStr
    current_password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str

    @model_validator(mode="after")
    def check_passwords_match(self) -> ChangePasswordRequest:
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")

        return self


class UserAuthHistoryResponse(BaseModel):
    user_agent: str
    auth_at: datetime
