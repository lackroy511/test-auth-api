from pathlib import Path
from typing import Literal

from pydantic import computed_field, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent.parent

RolesType = Literal["superuser", "staff", "subscriber"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR
    log_level: str

    redis_base_url: str

    postgres_db: str
    postgres_user: str
    postgres_password: str
    db_host: str
    db_port: int

    access_token_expire_minutes: int
    refresh_token_expire_days: int

    secret_key: str = Field(min_length=32)

    default_user_roles: list[RolesType] = ["superuser", "staff", "subscriber"]
    admin_role: RolesType = "superuser"

    admin_email: str
    admin_password: str

    access_cookie_name: str
    refresh_cookie_name: str
    cookie_secure: bool

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"  # noqa: E501

    @computed_field
    @property
    def access_token_ttl(self) -> int:
        return self.access_token_expire_minutes * 60

    @computed_field
    @property
    def refresh_token_ttl(self) -> int:
        return self.refresh_token_expire_days * 24 * 60 * 60


settings = Settings()  # ty: ignore
