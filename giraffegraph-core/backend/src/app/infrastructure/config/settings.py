from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.infrastructure.llm.anthropic_provider import AnthropicEffort


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "GiraffeGraph Core API"
    app_env: str = "development"
    repository_backend: str = "memory"
    auto_create_postgres_schema: bool = True
    auto_apply_postgres_migrations: bool | None = None
    allowed_origins: str = "http://localhost:3000"
    postgres_dsn: str = "postgresql://giraffegraph:giraffegraph@postgres:5432/giraffegraph"
    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "giraffegraph"
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_timeout_seconds: float = 30.0
    anthropic_api_key: str | None = None
    anthropic_timeout_seconds: float = 120.0
    anthropic_effort: AnthropicEffort = "low"
    default_llm_provider: str = "noop"
    default_llm_model: str | None = None
    default_extraction_prompt_version: str = "candidate_graph_extraction_v2"
    extraction_max_segments_per_call: int | None = Field(default=None, ge=1)
    processing_job_poll_interval_seconds: float = 2.0

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def normalized_postgres_dsn(self) -> str:
        if self.postgres_dsn.startswith("postgresql+psycopg://"):
            return self.postgres_dsn
        if self.postgres_dsn.startswith("postgresql://"):
            return self.postgres_dsn.replace("postgresql://", "postgresql+psycopg://", 1)
        return self.postgres_dsn

    @property
    def should_auto_apply_postgres_migrations(self) -> bool:
        if self.auto_apply_postgres_migrations is not None:
            return self.auto_apply_postgres_migrations
        return self.auto_create_postgres_schema


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
