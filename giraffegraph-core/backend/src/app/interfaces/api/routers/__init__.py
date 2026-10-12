from fastapi import APIRouter

from app.interfaces.api.routers.chains import router as chains_router
from app.interfaces.api.routers.commit import router as commit_router
from app.interfaces.api.routers.exploration import router as exploration_router
from app.interfaces.api.routers.extraction import router as extraction_router
from app.interfaces.api.routers.health import router as health_router
from app.interfaces.api.routers.ingestion import router as ingestion_router
from app.interfaces.api.routers.pipeline import router as pipeline_router
from app.interfaces.api.routers.pipeline_definitions import (
    router as pipeline_definitions_router,
)
from app.interfaces.api.routers.processing_jobs import router as processing_jobs_router
from app.interfaces.api.routers.projects import router as projects_router
from app.interfaces.api.routers.review import router as review_router
from app.interfaces.api.routers.schema import router as schema_router
from app.interfaces.api.routers.templates import router as templates_router

api_router = APIRouter()
api_router.include_router(chains_router)
api_router.include_router(commit_router)
api_router.include_router(extraction_router)
api_router.include_router(exploration_router)
api_router.include_router(health_router)
api_router.include_router(ingestion_router)
api_router.include_router(pipeline_definitions_router)
api_router.include_router(pipeline_router)
api_router.include_router(processing_jobs_router)
api_router.include_router(projects_router)
api_router.include_router(review_router)
api_router.include_router(schema_router)
api_router.include_router(templates_router)
