from pathlib import Path

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src_auth.core.config.settings import RolesType, settings

BASE_DIR = Path(__file__).parent.parent.parent.parent


class TestsSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        extra="ignore",
    )

    base_dir: Path = BASE_DIR

    auth_api_base_url: str = "http://auth_api:8000/api/auth"
    redis_base_url: str = "redis://auth_redis:6379"

    postgres_db: str
    postgres_user: str
    postgres_password: str
    db_host: str
    db_port: int

    default_user_roles: list[RolesType] = settings.default_user_roles
    admin_role: RolesType = settings.admin_role

    admin_email: str
    admin_password: str

    access_cookie_name: str
    refresh_cookie_name: str
    cookie_secure: bool

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.db_host}:{self.db_port}/{self.postgres_db}"  # noqa: E501


test_settings = TestsSettings()  # ty: ignore


print(test_settings.base_dir)
