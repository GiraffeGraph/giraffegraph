from datetime import datetime

from pydantic import BaseModel


class DomainTemplateResponse(BaseModel):
    template_id: str
    name: str
    slug: str
    description: str
    is_system: bool
    created_at: datetime
