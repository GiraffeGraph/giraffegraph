"""Add relation type merge keys.

Revision ID: 0005_relation_type_merge_keys
Revises: 0004_pipeline_definitions
Create Date: 2026-10-12 21:30:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0005_relation_type_merge_keys"
down_revision: str | None = "0004_pipeline_definitions"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "relation_types",
        sa.Column(
            "merge_keys",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )
    op.alter_column("relation_types", "merge_keys", server_default=None)


def downgrade() -> None:
    op.drop_column("relation_types", "merge_keys")
