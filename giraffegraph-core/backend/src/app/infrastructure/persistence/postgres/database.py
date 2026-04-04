from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.infrastructure.config.settings import get_settings


@lru_cache(maxsize=1)
def get_postgres_engine() -> Engine:
    settings = get_settings()
    return create_engine(
        settings.normalized_postgres_dsn,
        pool_pre_ping=True,
        future=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(
        bind=get_postgres_engine(),
        autoflush=False,
        expire_on_commit=False,
        future=True,
    )


def session_scope() -> Iterator[Session]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def dispose_postgres_engine() -> None:
    get_postgres_engine().dispose()
    get_postgres_engine.cache_clear()
    get_session_factory.cache_clear()
