from dataclasses import dataclass

from app.application.errors import NotFoundError
from app.application.ports.repositories import CanonicalGraphRepository, ProjectRepository
from app.domain.exploration.entities import (
    CanonicalNodeDetail,
    CanonicalNodeView,
    CanonicalRelationDetail,
    CanonicalRelationView,
    GraphOverview,
)


@dataclass(slots=True)
class GraphExplorationService:
    project_repository: ProjectRepository
    canonical_graph_repository: CanonicalGraphRepository

    def get_project_overview(self, project_id: str) -> GraphOverview:
        self._require_project(project_id)
        return self.canonical_graph_repository.get_project_overview(project_id)

    def list_nodes(
        self,
        project_id: str,
        *,
        node_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalNodeView]:
        self._require_project(project_id)
        return self.canonical_graph_repository.list_nodes(
            project_id,
            node_type=node_type.strip() if node_type else None,
            limit=limit,
        )

    def list_relations(
        self,
        project_id: str,
        *,
        relation_type: str | None = None,
        limit: int = 50,
    ) -> list[CanonicalRelationView]:
        self._require_project(project_id)
        return self.canonical_graph_repository.list_relations(
            project_id,
            relation_type=relation_type.strip() if relation_type else None,
            limit=limit,
        )

    def get_node_detail(
        self,
        project_id: str,
        *,
        node_type: str,
        merge_key: str,
    ) -> CanonicalNodeDetail:
        self._require_project(project_id)
        detail = self.canonical_graph_repository.get_node_detail(
            project_id,
            node_type=node_type.strip(),
            merge_key=merge_key,
        )
        if detail is None:
            raise NotFoundError(
                "Canonical node was not found for project "
                f"'{project_id}', node_type '{node_type}', merge_key '{merge_key}'."
            )
        return detail

    def get_relation_detail(
        self,
        project_id: str,
        *,
        relation_type: str,
        from_node_type: str,
        from_merge_key: str,
        to_node_type: str,
        to_merge_key: str,
    ) -> CanonicalRelationDetail:
        self._require_project(project_id)
        detail = self.canonical_graph_repository.get_relation_detail(
            project_id,
            relation_type=relation_type.strip(),
            from_node_type=from_node_type.strip(),
            from_merge_key=from_merge_key,
            to_node_type=to_node_type.strip(),
            to_merge_key=to_merge_key,
        )
        if detail is None:
            raise NotFoundError(
                "Canonical relation was not found for project "
                f"'{project_id}', relation_type '{relation_type}'."
            )
        return detail

    def _require_project(self, project_id: str) -> None:
        project = self.project_repository.get(project_id)
        if project is None:
            raise NotFoundError(f"Project '{project_id}' was not found.")
