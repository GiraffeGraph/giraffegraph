import pytest
from alembic import command as alembic_command

from app.infrastructure.persistence.postgres import migrations


class _FakeInspector:
    def __init__(self, table_names: set[str]) -> None:
        self._table_names = table_names

    def get_table_names(self) -> list[str]:
        return sorted(self._table_names)


def test_apply_postgres_migrations_stamps_existing_baseline_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = object()
    stamped: list[str] = []
    upgraded: list[str] = []

    monkeypatch.setattr(migrations, "_build_alembic_config", lambda: config)
    monkeypatch.setattr(migrations, "get_postgres_engine", lambda: object())
    monkeypatch.setattr(
        migrations,
        "inspect",
        lambda _: _FakeInspector(migrations.BASELINE_TABLES),
    )
    def fake_stamp(received_config: object, revision: str) -> None:
        assert received_config is config
        stamped.append(revision)

    def fake_upgrade(received_config: object, revision: str) -> None:
        assert received_config is config
        upgraded.append(revision)

    monkeypatch.setattr(alembic_command, "stamp", fake_stamp)
    monkeypatch.setattr(alembic_command, "upgrade", fake_upgrade)

    migrations.apply_postgres_migrations()

    assert stamped == [migrations.BASELINE_REVISION]
    assert upgraded == ["head"]


def test_apply_postgres_migrations_rejects_partial_baseline_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(migrations, "_build_alembic_config", lambda: object())
    monkeypatch.setattr(migrations, "get_postgres_engine", lambda: object())
    monkeypatch.setattr(
        migrations,
        "inspect",
        lambda _: _FakeInspector({"projects", "schema_versions"}),
    )

    with pytest.raises(RuntimeError):
        migrations.apply_postgres_migrations()
