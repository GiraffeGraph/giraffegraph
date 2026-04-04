from app.application.use_cases.commit_management import CommitManagementService
from app.application.use_cases.exploration_management import GraphExplorationService
from app.application.use_cases.extraction_management import ExtractionManagementService
from app.application.use_cases.ingestion_management import IngestionManagementService
from app.application.use_cases.pipeline_definition_management import (
    PipelineDefinitionManagementService,
)
from app.application.use_cases.pipeline_management import PipelineManagementService
from app.application.use_cases.processing_job_management import (
    ProcessingJobManagementService,
)
from app.application.use_cases.processing_job_queue_management import (
    ProcessingJobQueueService,
)
from app.application.use_cases.project_management import ProjectManagementService
from app.application.use_cases.review_management import ReviewManagementService
from app.application.use_cases.review_queue_management import ReviewQueueService
from app.application.use_cases.schema_management import SchemaManagementService
from app.application.use_cases.template_management import TemplateManagementService
from app.bootstrap.container import get_container


def get_commit_management_service() -> CommitManagementService:
    return get_container().commit_management_service


def get_extraction_management_service() -> ExtractionManagementService:
    return get_container().extraction_management_service


def get_graph_exploration_service() -> GraphExplorationService:
    return get_container().graph_exploration_service


def get_ingestion_management_service() -> IngestionManagementService:
    return get_container().ingestion_management_service


def get_pipeline_definition_management_service() -> PipelineDefinitionManagementService:
    return get_container().pipeline_definition_management_service


def get_pipeline_management_service() -> PipelineManagementService:
    return get_container().pipeline_management_service


def get_processing_job_management_service() -> ProcessingJobManagementService:
    return get_container().processing_job_management_service


def get_processing_job_queue_service() -> ProcessingJobQueueService:
    return get_container().processing_job_queue_service


def get_project_management_service() -> ProjectManagementService:
    return get_container().project_management_service


def get_template_management_service() -> TemplateManagementService:
    return get_container().template_management_service


def get_review_management_service() -> ReviewManagementService:
    return get_container().review_management_service


def get_review_queue_service() -> ReviewQueueService:
    return get_container().review_queue_service


def get_schema_management_service() -> SchemaManagementService:
    return get_container().schema_management_service
