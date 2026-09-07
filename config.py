# Author: Manali Mankad
# GitHub Issues Gateway service implementation
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str
    github_owner: str
    github_repo: str
    webhook_secret: str
    port: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
