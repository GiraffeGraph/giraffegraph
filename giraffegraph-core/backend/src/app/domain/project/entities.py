from dataclasses import dataclass, field
from datetime import UTC, datetime

from app.domain.shared.enums import ProjectStatus


@dataclass(slots=True, kw_only=True)
class Project:
    project_id: str
    name: str
    description: str | None = None
    template_id: str | None = None
    status: ProjectStatus = ProjectStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
