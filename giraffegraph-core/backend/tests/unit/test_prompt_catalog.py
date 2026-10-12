import pytest

from app.bootstrap.container import get_container
from app.infrastructure.config.settings import get_settings
from app.infrastructure.llm.prompt_catalog import RepositoryStructuredPromptCatalog


def test_container_uses_repository_backed_prompt_catalog(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("REPOSITORY_BACKEND", "memory")
    get_settings.cache_clear()
    get_container.cache_clear()

    try:
        container = get_container()
        prompt_catalog = container.extraction_management_service.prompt_catalog
        assert isinstance(prompt_catalog, RepositoryStructuredPromptCatalog)

        default_version = container.extraction_management_service.default_extraction_prompt_version
        assert default_version == "candidate_graph_extraction_v2"
        prompt = prompt_catalog.get(
            prompt_key="candidate_graph_extraction",
            version=default_version,
        )
        assert prompt is not None
        assert prompt.schema_name == "candidate_graph_extraction_v2"
        assert "Return a JSON object" in prompt.prompt_text
        assert "must match a schema name or alias (case-insensitive)" in prompt.prompt_text

        first_version = prompt_catalog.get(
            prompt_key="candidate_graph_extraction",
            version="candidate_graph_extraction_v1",
        )
        assert first_version is not None
        assert first_version.schema_name == "candidate_graph_extraction_v1"
        assert "must exactly match schema names (case-sensitive)" in first_version.prompt_text
    finally:
        get_container.cache_clear()
        get_settings.cache_clear()
