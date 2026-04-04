from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.shared.enums import ProjectStatus


class ProjectCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    template_id: str | None = None


class ProjectResponse(BaseModel):
    project_id: str
    name: str
    description: str | None
    template_id: str | None
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
