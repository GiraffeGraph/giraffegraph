import importlib.util
import io
import re
from pathlib import Path
from types import ModuleType

from alembic.operations import Operations
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateTable

from app.infrastructure.persistence.postgres.models import ReviewDecisionModel

MIGRATIONS_ROOT = Path(__file__).resolve().parents[2] / "migrations"
MIGRATION_PATH = MIGRATIONS_ROOT / "versions" / "0006_add_review_decisions.py"


def _load_migration() -> ModuleType:
    spec = importlib.util.spec_from_file_location("review_decisions_migration", MIGRATION_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _render_upgrade_sql(module: ModuleType) -> str:
    buffer = io.StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql",
        opts={"as_sql": True, "output_buffer": buffer},
    )
    with Operations.context(context):
        module.upgrade()
    return buffer.getvalue()


def _table_definition_lines(sql: str) -> list[str]:
    match = re.search(r"CREATE TABLE review_decisions \((.*?)\n\)", sql, flags=re.DOTALL)
    assert match is not None
    return sorted(
        line.strip().rstrip(",") for line in match.group(1).splitlines() if line.strip()
    )


def test_review_decisions_migration_creates_the_table_the_model_declares() -> None:
    migration_sql = _render_upgrade_sql(_load_migration())
    model_sql = str(
        CreateTable(ReviewDecisionModel.__table__).compile(dialect=postgresql.dialect())
    )

    assert _table_definition_lines(migration_sql) == _table_definition_lines(model_sql)


def test_review_decisions_migration_is_the_single_head_after_relation_merge_keys() -> None:
    module = _load_migration()
    script_directory = ScriptDirectory(str(MIGRATIONS_ROOT))

    assert module.down_revision == "0005_relation_type_merge_keys"
    assert script_directory.get_heads() == [module.revision]
