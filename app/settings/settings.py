from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    DATABASE_URL: str = Field(default="sqlite:///./dev.db")
    API_TOKEN: SecretStr = Field(default=SecretStr("supersecret"))
