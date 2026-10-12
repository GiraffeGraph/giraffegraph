"""Fixtures for tests that run the application against real Postgres and Neo4j.

Tests marked `real_db` are skipped unless these variables point at running servers:

  GG_TEST_POSTGRES_DSN    e.g. postgresql://user:password@127.0.0.1:55432/postgres
  GG_TEST_NEO4J_URI       e.g. bolt://127.0.0.1:57687
  GG_TEST_NEO4J_PASSWORD
  GG_TEST_NEO4J_USERNAME  optional, defaults to neo4j

The Postgres role must be allowed to create databases: every use gets its own scratch
database, so the database named in the DSN is never written to. Neo4j has a single
database, so the graph written for the test projects is deleted when the session ends.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from neo4j import GraphDatabase
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine, make_url

from app.bootstrap.app_factory import create_app
from app.bootstrap.container import get_container
from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.neo4j.database import get_neo4j_driver
from app.infrastructure.persistence.postgres.database import (
    get_postgres_engine,
    get_session_factory,
)

POSTGRES_DSN_VARIABLE = "GG_TEST_POSTGRES_DSN"
NEO4J_URI_VARIABLE = "GG_TEST_NEO4J_URI"
NEO4J_USERNAME_VARIABLE = "GG_TEST_NEO4J_USERNAME"
NEO4J_PASSWORD_VARIABLE = "GG_TEST_NEO4J_PASSWORD"
REQUIRED_VARIABLES = (POSTGRES_DSN_VARIABLE, NEO4J_URI_VARIABLE, NEO4J_PASSWORD_VARIABLE)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    missing = [name for name in REQUIRED_VARIABLES if not os.environ.get(name)]
    if not missing:
        return
    skip = pytest.mark.skip(reason="real databases are not configured: set " + ", ".join(missing))
    for item in items:
        if "real_db" in item.keywords:
            item.add_marker(skip)


def _admin_url() -> URL:
    url = make_url(os.environ[POSTGRES_DSN_VARIABLE])
    if url.drivername == "postgresql":
        url = url.set(drivername="postgresql+psycopg")
    return url


def _neo4j_auth() -> tuple[str, str]:
    return (
        os.environ.get(NEO4J_USERNAME_VARIABLE, "neo4j"),
        os.environ[NEO4J_PASSWORD_VARIABLE],
    )


def _clear_backend_caches() -> None:
    get_container.cache_clear()
    get_settings.cache_clear()
    get_session_factory.cache_clear()
    get_postgres_engine.cache_clear()
    get_neo4j_driver.cache_clear()


def _delete_project_graphs(project_ids: list[str]) -> None:
    if not project_ids:
        return
    with GraphDatabase.driver(os.environ[NEO4J_URI_VARIABLE], auth=_neo4j_auth()) as driver:
        driver.execute_query(
            """
            MATCH (su:SourceUnit) WHERE su.project_id IN $project_ids
            OPTIONAL MATCH (su)-[:HAS_SEGMENT]->(sg:Segment)
            DETACH DELETE su, sg
            """,
            project_ids=project_ids,
        )
        driver.execute_query(
            "MATCH (n) WHERE n.project_id IN $project_ids DETACH DELETE n",
            project_ids=project_ids,
        )


@contextmanager
def scratch_postgres_database() -> Iterator[str]:
    """Create an empty database, yield its DSN, then drop it with the graphs of its projects."""
    admin_url = _admin_url()
    database_name = f"gg_realdb_{uuid4().hex}"
    scratch_url = admin_url.set(database=database_name)
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
        try:
            yield scratch_url.render_as_string(hide_password=False)
        finally:
            scratch_engine = create_engine(scratch_url)
            try:
                with scratch_engine.connect() as connection:
                    has_projects = connection.execute(
                        text("SELECT to_regclass('public.projects') IS NOT NULL")
                    ).scalar_one()
                    project_ids = (
                        list(connection.execute(text("SELECT project_id FROM projects")).scalars())
                        if has_projects
                        else []
                    )
            finally:
                scratch_engine.dispose()
            _delete_project_graphs(project_ids)
            with admin_engine.connect() as connection:
                connection.execute(text(f'DROP DATABASE "{database_name}" WITH (FORCE)'))
    finally:
        admin_engine.dispose()


@contextmanager
def real_backend_environment(postgres_dsn: str) -> Iterator[None]:
    """Point the application settings at the given Postgres database and the test Neo4j."""
    username, password = _neo4j_auth()
    overrides = {
        "REPOSITORY_BACKEND": "postgres",
        "AUTO_APPLY_POSTGRES_MIGRATIONS": "true",
        "POSTGRES_DSN": postgres_dsn,
        "NEO4J_URI": os.environ[NEO4J_URI_VARIABLE],
        "NEO4J_USERNAME": username,
        "NEO4J_PASSWORD": password,
        # Empty keys keep the hosted providers unregistered: these tests never call a model.
        "OPENAI_API_KEY": "",
        "ANTHROPIC_API_KEY": "",
        "DEFAULT_LLM_PROVIDER": "noop",
    }
    with pytest.MonkeyPatch.context() as monkeypatch:
        for name, value in overrides.items():
            monkeypatch.setenv(name, value)
        _clear_backend_caches()
        try:
            yield
        finally:
            get_postgres_engine().dispose()
            get_neo4j_driver().close()
            _clear_backend_caches()
    _clear_backend_caches()


@pytest.fixture(scope="session")
def real_db_postgres_dsn() -> Iterator[str]:
    with scratch_postgres_database() as dsn:
        yield dsn


@pytest.fixture
def real_db_client(real_db_postgres_dsn: str) -> Iterator[TestClient]:
    """Application on Postgres + Neo4j, started through its lifespan (migrations included)."""
    with real_backend_environment(real_db_postgres_dsn), TestClient(create_app()) as client:
        yield client


@pytest.fixture
def real_db_empty_engine() -> Iterator[Engine]:
    """Application settings pointed at a database that has no tables yet."""
    with scratch_postgres_database() as dsn, real_backend_environment(dsn):
        yield get_postgres_engine()
