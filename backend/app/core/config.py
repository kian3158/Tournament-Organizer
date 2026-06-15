from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env."""

    database_url: str = "sqlite:///./test.db"
    # Dev default only — override SECRET_KEY in production (use 32+ random bytes).
    secret_key: str = "dev-secret-change-me-in-production-0123456789"
    access_token_expire_minutes: int = 60 * 24
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
