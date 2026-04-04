from functools import lru_cache

from neo4j import Driver, GraphDatabase

from app.infrastructure.config.settings import get_settings


@lru_cache(maxsize=1)
def get_neo4j_driver() -> Driver:
    settings = get_settings()
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )


def dispose_neo4j_driver() -> None:
    get_neo4j_driver().close()
    get_neo4j_driver.cache_clear()
