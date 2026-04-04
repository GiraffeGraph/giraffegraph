from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config.settings import get_settings
from app.infrastructure.persistence.neo4j.database import dispose_neo4j_driver
from app.infrastructure.persistence.postgres.database import dispose_postgres_engine
from app.infrastructure.persistence.postgres.migrations import apply_postgres_migrations
from app.interfaces.api.error_handlers import register_error_handlers
from app.interfaces.api.routers import api_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    if (
        settings.repository_backend == "postgres"
        and settings.should_auto_apply_postgres_migrations
    ):
        apply_postgres_migrations()
    yield
    dispose_neo4j_driver()
    if settings.repository_backend == "postgres":
        dispose_postgres_engine()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Generic graph production engine backend.",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(api_router)
    return app
