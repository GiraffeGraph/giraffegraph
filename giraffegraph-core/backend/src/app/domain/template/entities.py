from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True, kw_only=True)
class DomainTemplate:
    template_id: str
    name: str
    slug: str
    description: str
    is_system: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
