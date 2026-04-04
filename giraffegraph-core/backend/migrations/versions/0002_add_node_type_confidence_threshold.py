"""Add node type confidence threshold.

Revision ID: 0002_node_confidence_threshold
Revises: 0001_initial_metadata_schema
Create Date: 2026-03-15 12:10:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_node_confidence_threshold"
down_revision: str | None = "0001_initial_metadata_schema"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "node_types",
        sa.Column(
            "confidence_threshold",
            sa.Float(),
            nullable=False,
            server_default="0.5",
        ),
    )
    op.alter_column("node_types", "confidence_threshold", server_default=None)


def downgrade() -> None:
    op.drop_column("node_types", "confidence_threshold")
