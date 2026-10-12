import logging

import pytest
from alembic import command as alembic_command
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, inspect, text

from app.infrastructure.persistence.postgres.database import get_session_factory
from app.infrastructure.persistence.postgres.migrations import (
    _build_alembic_config,
    apply_postgres_migrations,
)
from app.infrastructure.persistence.postgres.models import Base
from app.infrastructure.persistence.postgres.repositories import PostgresSchemaRepository

pytestmark = pytest.mark.real_db


def _head_revision() -> str | None:
    return ScriptDirectory.from_config(_build_alembic_config()).get_current_head()


def _current_revision(engine: Engine) -> str | None:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def _schema_differences(engine: Engine) -> list[object]:
    with engine.connect() as connection:
        context = MigrationContext.configure(connection, opts={"compare_type": True})
        return list(compare_metadata(context, Base.metadata))


def test_migration_chain_on_empty_database_matches_the_orm_models(
    real_db_empty_engine: Engine,
) -> None:
    apply_postgres_migrations()

    assert _current_revision(real_db_empty_engine) == _head_revision()
    assert _schema_differences(real_db_empty_engine) == []
    assert set(inspect(real_db_empty_engine).get_table_names()) == {
        *Base.metadata.tables,
        "alembic_version",
    }


def test_merge_keys_migration_backfills_relation_types_that_already_exist(
    real_db_empty_engine: Engine,
) -> None:
    config = _build_alembic_config()
    alembic_command.upgrade(config, "0004_pipeline_definitions")
    with real_db_empty_engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO projects (project_id, name, status, created_at, updated_at) "
                "VALUES ('realdb-migration-project', 'Existing project', 'ACTIVE', now(), now())"
            )
        )
        connection.execute(
            text(
                "INSERT INTO schema_versions (schema_version_id, project_id, version_no, status, "
                "created_at) VALUES ('s1', 'realdb-migration-project', 1, 'DRAFT', now())"
            )
        )
        connection.execute(
            text(
                "INSERT INTO relation_types (relation_type_id, schema_version_id, name, "
                "from_type, to_type, description, directional, aliases, extraction_hints, "
                "required_properties, confidence_threshold, is_active) VALUES "
                "('r1', 's1', 'KNOWS', 'Person', 'Person', 'Knows', true, '[]', '[]', '[]', "
                "0.7, true)"
            )
        )

    alembic_command.upgrade(config, "head")

    relation_types = PostgresSchemaRepository(
        session_factory=get_session_factory()
    ).list_relation_types("s1")
    assert [(item.name, item.merge_keys) for item in relation_types] == [("KNOWS", [])]
    assert _schema_differences(real_db_empty_engine) == []


def test_migration_chain_downgrades_to_an_empty_schema_and_upgrades_again(
    real_db_empty_engine: Engine,
) -> None:
    config = _build_alembic_config()
    alembic_command.upgrade(config, "head")

    alembic_command.downgrade(config, "base")

    assert inspect(real_db_empty_engine).get_table_names() == ["alembic_version"]
    alembic_command.upgrade(config, "head")
    assert _current_revision(real_db_empty_engine) == _head_revision()
    assert _schema_differences(real_db_empty_engine) == []


def test_migrations_at_startup_leave_application_loggers_enabled(
    real_db_empty_engine: Engine,
) -> None:
    del real_db_empty_engine
    server_logger = logging.getLogger("uvicorn.error")
    server_logger.disabled = False

    apply_postgres_migrations()

    assert server_logger.disabled is False
