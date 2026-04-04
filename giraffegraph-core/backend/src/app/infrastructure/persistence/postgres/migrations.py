from pathlib import Path

from alembic import command as alembic_command
from alembic.config import Config
from sqlalchemy import inspect

from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.postgres.database import get_postgres_engine

BASELINE_REVISION = "0001_initial_metadata_schema"
BASELINE_TABLES = {
    "projects",
    "structured_prompts",
    "schema_versions",
    "node_types",
    "relation_types",
    "property_definitions",
    "source_units",
    "segments",
    "processing_runs",
    "extraction_executions",
    "candidate_nodes",
    "candidate_relations",
    "validation_results",
    "review_items",
    "graph_deltas",
}


def apply_postgres_migrations() -> None:
    config = _build_alembic_config()
    engine = get_postgres_engine()
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    if "alembic_version" not in existing_tables:
        existing_managed_tables = existing_tables & BASELINE_TABLES
        if existing_managed_tables:
            missing_tables = BASELINE_TABLES - existing_managed_tables
            if missing_tables:
                raise RuntimeError(
                    "Postgres schema is partially initialized outside Alembic; "
                    "refusing to auto-adopt a partial metadata schema. Missing tables: "
                    + ", ".join(sorted(missing_tables))
                    + "."
                )
            alembic_command.stamp(config, BASELINE_REVISION)

    alembic_command.upgrade(config, "head")


def _build_alembic_config() -> Config:
    backend_root = _backend_root()
    config = Config(str(backend_root / "alembic.ini"))
    config.set_main_option("script_location", str(backend_root / "migrations"))
    config.set_main_option("sqlalchemy.url", get_settings().normalized_postgres_dsn)
    return config


def _backend_root() -> Path:
    return Path(__file__).resolve().parents[5]
