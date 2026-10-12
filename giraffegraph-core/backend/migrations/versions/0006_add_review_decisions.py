"""Add review decisions.

Revision ID: 0006_review_decisions
Revises: 0005_relation_type_merge_keys
Create Date: 2026-10-12 23:00:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0006_review_decisions"
down_revision: str | None = "0005_relation_type_merge_keys"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_decisions",
        sa.Column("decision_id", sa.String(length=36), nullable=False),
        sa.Column("review_item_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("item_ref", sa.String(length=36), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("reviewer_id", sa.String(length=120), nullable=False),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("before_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("decision_id"),
    )
    op.create_index(
        "ix_review_decisions_run_decided_at",
        "review_decisions",
        ["run_id", "decided_at"],
        unique=False,
    )
    op.create_index(
        "ix_review_decisions_review_item_decided_at",
        "review_decisions",
        ["review_item_id", "decided_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_review_decisions_review_item_decided_at", table_name="review_decisions")
    op.drop_index("ix_review_decisions_run_decided_at", table_name="review_decisions")
    op.drop_table("review_decisions")
