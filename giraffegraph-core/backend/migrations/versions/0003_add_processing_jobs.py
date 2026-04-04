"""Add processing jobs.

Revision ID: 0003_processing_jobs
Revises: 0002_node_confidence_threshold
Create Date: 2026-03-15 13:20:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_processing_jobs"
down_revision: str | None = "0002_node_confidence_threshold"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processing_jobs",
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("source_unit_id", sa.String(length=36), nullable=False),
        sa.Column(
            "job_type",
            sa.Enum(
                "extract_candidates",
                name="processingjobtype",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "succeeded",
                "failed",
                name="processingjobstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.ForeignKeyConstraint(["source_unit_id"], ["source_units.source_unit_id"]),
        sa.PrimaryKeyConstraint("job_id"),
    )
    op.create_index(
        "ix_processing_jobs_run_created_at",
        "processing_jobs",
        ["run_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "ix_processing_jobs_status_created_at",
        "processing_jobs",
        ["status", "created_at"],
        unique=False,
    )
    op.alter_column("processing_jobs", "attempt_count", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_processing_jobs_status_created_at", table_name="processing_jobs")
    op.drop_index("ix_processing_jobs_run_created_at", table_name="processing_jobs")
    op.drop_table("processing_jobs")
