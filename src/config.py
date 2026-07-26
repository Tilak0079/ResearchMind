"""
Central place for all app configuration.

Instead of scattering `os.environ.get("SOME_VAR")` calls across the codebase,
every other module imports the `settings` object from here. This makes it
obvious what environment variables the app needs, and gives us validation
for free (e.g. if POSTGRES_PORT isn't a valid integer, this will fail loudly
at startup instead of silently breaking later).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Defines every environment variable the app depends on.
    Values are automatically loaded from the .env file at project root.
    """

    # --- Application ---
    app_env: str = "development"
    log_level: str = "INFO"

    # --- PostgreSQL ---
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "rag_assistant"
    postgres_user: str = "rag_user"
    postgres_password: str = "changeme"

    # --- Qdrant ---
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # --- Redis ---
    redis_host: str = "localhost"
    redis_port: int = 6379

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- MinIO ---
    minio_root_user: str = "minio_admin"
    minio_root_password: str = "changeme_minio"
    minio_endpoint: str = "localhost:9000"
    minio_bucket_name: str = "papers"


# Create ONE shared instance that the rest of the app imports.
# Example usage elsewhere: `from src.config import settings` then `settings.postgres_host`
settings = Settings()