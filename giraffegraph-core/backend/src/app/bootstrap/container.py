from dataclasses import dataclass
from functools import lru_cache

from app.application.ports.llm_provider import LLMProvider
from app.application.ports.repositories import (
    CandidateNodeRepository,
    CandidateRelationRepository,
    CanonicalGraphRepository,
    ExtractionExecutionRepository,
    GraphDeltaRepository,
    PipelineDefinitionRepository,
    ProcessingJobQueueRepository,
    ProcessingJobRepository,
    ProcessingRunRepository,
    ProjectRepository,
    ReviewItemRepository,
    ReviewQueueRepository,
    SchemaRepository,
    SegmentRepository,
    SourceUnitRepository,
    StructuredPromptRepository,
    ValidationResultRepository,
)
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
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.noop_provider import NoOpLLMProvider
from app.infrastructure.llm.openai_provider import OpenAILLMProvider
from app.infrastructure.llm.prompt_catalog import (
    RepositoryStructuredPromptCatalog,
    seed_default_structured_prompts,
)
from app.infrastructure.llm.provider_registry import StaticLLMProviderRegistry
from app.infrastructure.persistence.memory.repositories import (
    InMemoryCandidateNodeRepository,
    InMemoryCandidateRelationRepository,
    InMemoryCanonicalGraphRepository,
    InMemoryExtractionExecutionRepository,
    InMemoryGraphDeltaRepository,
    InMemoryPipelineDefinitionRepository,
    InMemoryProcessingJobQueueRepository,
    InMemoryProcessingJobRepository,
    InMemoryProcessingRunRepository,
    InMemoryProjectRepository,
    InMemoryReviewItemRepository,
    InMemoryReviewQueueRepository,
    InMemorySchemaRepository,
    InMemorySegmentRepository,
    InMemorySourceUnitRepository,
    InMemoryStructuredPromptRepository,
    InMemoryValidationResultRepository,
)
from app.infrastructure.persistence.memory.store import InMemoryStore
from app.infrastructure.persistence.neo4j.database import get_neo4j_driver
from app.infrastructure.persistence.neo4j.repositories import Neo4jCanonicalGraphRepository
from app.infrastructure.persistence.postgres.database import get_session_factory
from app.infrastructure.persistence.postgres.repositories import (
    PostgresCandidateNodeRepository,
    PostgresCandidateRelationRepository,
    PostgresExtractionExecutionRepository,
    PostgresGraphDeltaRepository,
    PostgresPipelineDefinitionRepository,
    PostgresProcessingJobQueueRepository,
    PostgresProcessingJobRepository,
    PostgresProcessingRunRepository,
    PostgresProjectRepository,
    PostgresReviewItemRepository,
    PostgresReviewQueueRepository,
    PostgresSchemaRepository,
    PostgresSegmentRepository,
    PostgresSourceUnitRepository,
    PostgresStructuredPromptRepository,
    PostgresValidationResultRepository,
)
from app.infrastructure.template.catalog import (
    SYSTEM_DOMAIN_TEMPLATES,
    StaticDomainTemplateCatalog,
)


@dataclass(slots=True)
class ApplicationContainer:
    project_management_service: ProjectManagementService
    template_management_service: TemplateManagementService
    schema_management_service: SchemaManagementService
    ingestion_management_service: IngestionManagementService
    pipeline_definition_management_service: PipelineDefinitionManagementService
    extraction_management_service: ExtractionManagementService
    processing_job_management_service: ProcessingJobManagementService
    processing_job_queue_service: ProcessingJobQueueService
    pipeline_management_service: PipelineManagementService
    review_management_service: ReviewManagementService
    review_queue_service: ReviewQueueService
    commit_management_service: CommitManagementService
    graph_exploration_service: GraphExplorationService


@lru_cache(maxsize=1)
def get_container() -> ApplicationContainer:
    settings = get_settings()
    template_catalog = StaticDomainTemplateCatalog(templates=SYSTEM_DOMAIN_TEMPLATES)
    project_repository: ProjectRepository
    schema_repository: SchemaRepository
    source_unit_repository: SourceUnitRepository
    segment_repository: SegmentRepository
    processing_run_repository: ProcessingRunRepository
    pipeline_definition_repository: PipelineDefinitionRepository
    processing_job_repository: ProcessingJobRepository
    processing_job_queue_repository: ProcessingJobQueueRepository
    candidate_node_repository: CandidateNodeRepository
    candidate_relation_repository: CandidateRelationRepository
    extraction_execution_repository: ExtractionExecutionRepository
    structured_prompt_repository: StructuredPromptRepository
    validation_result_repository: ValidationResultRepository
    review_item_repository: ReviewItemRepository
    review_queue_repository: ReviewQueueRepository
    graph_delta_repository: GraphDeltaRepository
    canonical_graph_repository: CanonicalGraphRepository

    llm_providers: list[LLMProvider] = [NoOpLLMProvider()]
    if settings.openai_api_key is not None and settings.openai_api_key.strip() != "":
        llm_providers.append(
            OpenAILLMProvider(
                api_key=settings.openai_api_key,
                base_url=settings.openai_base_url,
                timeout_seconds=settings.openai_timeout_seconds,
            )
        )
    llm_provider_registry = StaticLLMProviderRegistry(providers=llm_providers)
    prompt_catalog: RepositoryStructuredPromptCatalog

    if settings.repository_backend == "postgres":
        session_factory = get_session_factory()
        project_repository = PostgresProjectRepository(session_factory=session_factory)
        schema_repository = PostgresSchemaRepository(session_factory=session_factory)
        source_unit_repository = PostgresSourceUnitRepository(session_factory=session_factory)
        segment_repository = PostgresSegmentRepository(session_factory=session_factory)
        processing_run_repository = PostgresProcessingRunRepository(
            session_factory=session_factory
        )
        pipeline_definition_repository = PostgresPipelineDefinitionRepository(
            session_factory=session_factory
        )
        processing_job_repository = PostgresProcessingJobRepository(
            session_factory=session_factory
        )
        processing_job_queue_repository = PostgresProcessingJobQueueRepository(
            session_factory=session_factory
        )
        candidate_node_repository = PostgresCandidateNodeRepository(
            session_factory=session_factory
        )
        candidate_relation_repository = PostgresCandidateRelationRepository(
            session_factory=session_factory
        )
        extraction_execution_repository = PostgresExtractionExecutionRepository(
            session_factory=session_factory
        )
        structured_prompt_repository = PostgresStructuredPromptRepository(
            session_factory=session_factory
        )
        validation_result_repository = PostgresValidationResultRepository(
            session_factory=session_factory
        )
        review_item_repository = PostgresReviewItemRepository(session_factory=session_factory)
        review_queue_repository = PostgresReviewQueueRepository(
            session_factory=session_factory
        )
        graph_delta_repository = PostgresGraphDeltaRepository(session_factory=session_factory)
        canonical_graph_repository = Neo4jCanonicalGraphRepository(
            driver=get_neo4j_driver()
        )
    else:
        store = InMemoryStore()
        project_repository = InMemoryProjectRepository(store=store)
        schema_repository = InMemorySchemaRepository(store=store)
        source_unit_repository = InMemorySourceUnitRepository(store=store)
        segment_repository = InMemorySegmentRepository(store=store)
        processing_run_repository = InMemoryProcessingRunRepository(store=store)
        pipeline_definition_repository = InMemoryPipelineDefinitionRepository(store=store)
        processing_job_repository = InMemoryProcessingJobRepository(store=store)
        processing_job_queue_repository = InMemoryProcessingJobQueueRepository(store=store)
        structured_prompt_repository = InMemoryStructuredPromptRepository(store=store)
        candidate_node_repository = InMemoryCandidateNodeRepository(store=store)
        candidate_relation_repository = InMemoryCandidateRelationRepository(store=store)
        extraction_execution_repository = InMemoryExtractionExecutionRepository(store=store)
        validation_result_repository = InMemoryValidationResultRepository(store=store)
        review_item_repository = InMemoryReviewItemRepository(store=store)
        review_queue_repository = InMemoryReviewQueueRepository(store=store)
        graph_delta_repository = InMemoryGraphDeltaRepository(store=store)
        canonical_graph_repository = InMemoryCanonicalGraphRepository(store=store)

    seed_default_structured_prompts(structured_prompt_repository)
    prompt_catalog = RepositoryStructuredPromptCatalog(repository=structured_prompt_repository)
    extraction_management_service = ExtractionManagementService(
        processing_run_repository=processing_run_repository,
        source_unit_repository=source_unit_repository,
        segment_repository=segment_repository,
        schema_repository=schema_repository,
        candidate_node_repository=candidate_node_repository,
        candidate_relation_repository=candidate_relation_repository,
        extraction_execution_repository=extraction_execution_repository,
        provider_registry=llm_provider_registry,
        prompt_catalog=prompt_catalog,
        default_llm_provider=settings.default_llm_provider,
        default_llm_model=settings.default_llm_model,
        default_extraction_prompt_version=settings.default_extraction_prompt_version,
    )
    pipeline_management_service = PipelineManagementService(
        source_unit_repository=source_unit_repository,
        segment_repository=segment_repository,
        processing_run_repository=processing_run_repository,
        schema_repository=schema_repository,
        candidate_node_repository=candidate_node_repository,
        candidate_relation_repository=candidate_relation_repository,
        validation_result_repository=validation_result_repository,
        review_item_repository=review_item_repository,
        canonical_graph_repository=canonical_graph_repository,
    )
    commit_management_service = CommitManagementService(
        processing_run_repository=processing_run_repository,
        source_unit_repository=source_unit_repository,
        segment_repository=segment_repository,
        candidate_node_repository=candidate_node_repository,
        candidate_relation_repository=candidate_relation_repository,
        review_item_repository=review_item_repository,
        graph_delta_repository=graph_delta_repository,
        canonical_graph_repository=canonical_graph_repository,
    )

    return ApplicationContainer(
        project_management_service=ProjectManagementService(
            project_repository=project_repository,
            template_catalog=template_catalog,
        ),
        template_management_service=TemplateManagementService(
            template_catalog=template_catalog
        ),
        schema_management_service=SchemaManagementService(
            project_repository=project_repository,
            schema_repository=schema_repository,
            pipeline_definition_repository=pipeline_definition_repository,
        ),
        ingestion_management_service=IngestionManagementService(
            project_repository=project_repository,
            schema_repository=schema_repository,
            source_unit_repository=source_unit_repository,
            processing_run_repository=processing_run_repository,
            pipeline_definition_repository=pipeline_definition_repository,
        ),
        pipeline_definition_management_service=PipelineDefinitionManagementService(
            schema_repository=schema_repository,
            pipeline_definition_repository=pipeline_definition_repository,
        ),
        extraction_management_service=extraction_management_service,
        processing_job_management_service=ProcessingJobManagementService(
            processing_run_repository=processing_run_repository,
            pipeline_definition_repository=pipeline_definition_repository,
            processing_job_repository=processing_job_repository,
            extraction_management_service=extraction_management_service,
            pipeline_management_service=pipeline_management_service,
            commit_management_service=commit_management_service,
        ),
        processing_job_queue_service=ProcessingJobQueueService(
            project_repository=project_repository,
            processing_job_queue_repository=processing_job_queue_repository,
        ),
        pipeline_management_service=pipeline_management_service,
        review_management_service=ReviewManagementService(
            review_item_repository=review_item_repository,
            candidate_node_repository=candidate_node_repository,
            candidate_relation_repository=candidate_relation_repository,
            processing_run_repository=processing_run_repository,
            schema_repository=schema_repository,
        ),
        review_queue_service=ReviewQueueService(
            project_repository=project_repository,
            review_queue_repository=review_queue_repository,
        ),
        commit_management_service=commit_management_service,
        graph_exploration_service=GraphExplorationService(
            project_repository=project_repository,
            canonical_graph_repository=canonical_graph_repository,
        ),
    )
