"""Add pipeline definitions.

Revision ID: 0004_pipeline_definitions
Revises: 0003_processing_jobs
Create Date: 2026-03-15 16:40:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0004_pipeline_definitions"
down_revision: str | None = "0003_processing_jobs"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "pipeline_definitions",
        sa.Column("pipeline_definition_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("steps_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["schema_version_id"], ["schema_versions.schema_version_id"]),
        sa.PrimaryKeyConstraint("pipeline_definition_id"),
        sa.UniqueConstraint(
            "schema_version_id",
            "version",
            name="uq_pipeline_definition_version",
        ),
    )
    op.create_index(
        "ix_pipeline_definitions_schema_created_at",
        "pipeline_definitions",
        ["schema_version_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_pipeline_definitions_schema_created_at", table_name="pipeline_definitions")
    op.drop_table("pipeline_definitions")
