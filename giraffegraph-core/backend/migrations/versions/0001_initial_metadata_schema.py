"""Initial metadata schema.

Revision ID: 0001_initial_metadata_schema
Revises:
Create Date: 2026-03-15 12:00:00.000000
"""

from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial_metadata_schema"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("template_id", sa.String(length=120), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "active",
                "archived",
                name="projectstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("project_id"),
    )
    op.create_table(
        "structured_prompts",
        sa.Column("prompt_id", sa.String(length=36), nullable=False),
        sa.Column("prompt_key", sa.String(length=120), nullable=False),
        sa.Column("version", sa.String(length=120), nullable=False),
        sa.Column("schema_name", sa.String(length=120), nullable=False),
        sa.Column("prompt_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("prompt_id"),
        sa.UniqueConstraint(
            "prompt_key",
            "version",
            name="uq_structured_prompt_version",
        ),
    )
    op.create_table(
        "schema_versions",
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "published",
                "active",
                "retired",
                name="schemastatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.PrimaryKeyConstraint("schema_version_id"),
        sa.UniqueConstraint("project_id", "version_no", name="uq_schema_version"),
    )
    op.create_table(
        "node_types",
        sa.Column("node_type_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_core", sa.Boolean(), nullable=False),
        sa.Column("merge_keys", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("aliases", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "extraction_hints",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["schema_version_id"],
            ["schema_versions.schema_version_id"],
        ),
        sa.PrimaryKeyConstraint("node_type_id"),
        sa.UniqueConstraint("schema_version_id", "name", name="uq_node_type_name"),
    )
    op.create_table(
        "relation_types",
        sa.Column("relation_type_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("from_type", sa.String(length=80), nullable=False),
        sa.Column("to_type", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("directional", sa.Boolean(), nullable=False),
        sa.Column("aliases", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "extraction_hints",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "required_properties",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("confidence_threshold", sa.Float(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["schema_version_id"],
            ["schema_versions.schema_version_id"],
        ),
        sa.PrimaryKeyConstraint("relation_type_id"),
        sa.UniqueConstraint(
            "schema_version_id",
            "name",
            name="uq_relation_type_name",
        ),
    )
    op.create_table(
        "property_definitions",
        sa.Column("property_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("owner_kind", sa.String(length=20), nullable=False),
        sa.Column("owner_type_name", sa.String(length=120), nullable=False),
        sa.Column("node_type_id", sa.String(length=36), nullable=True),
        sa.Column("relation_type_id", sa.String(length=36), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("data_type", sa.String(length=50), nullable=False),
        sa.Column("required", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("default_value", sa.Text(), nullable=True),
        sa.Column("enum_values", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["node_type_id"], ["node_types.node_type_id"]),
        sa.ForeignKeyConstraint(["relation_type_id"], ["relation_types.relation_type_id"]),
        sa.ForeignKeyConstraint(
            ["schema_version_id"],
            ["schema_versions.schema_version_id"],
        ),
        sa.PrimaryKeyConstraint("property_id"),
    )
    op.create_table(
        "source_units",
        sa.Column("source_unit_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("raw_content", sa.Text(), nullable=False),
        sa.Column("sequence_no", sa.Integer(), nullable=True),
        sa.Column("external_ref", sa.String(length=200), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "draft",
                "ready",
                "processing",
                "processed",
                "failed",
                name="sourceunitstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.ForeignKeyConstraint(
            ["schema_version_id"],
            ["schema_versions.schema_version_id"],
        ),
        sa.PrimaryKeyConstraint("source_unit_id"),
    )
    op.create_table(
        "segments",
        sa.Column("segment_id", sa.String(length=36), nullable=False),
        sa.Column("source_unit_id", sa.String(length=36), nullable=False),
        sa.Column("segment_order", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(["source_unit_id"], ["source_units.source_unit_id"]),
        sa.PrimaryKeyConstraint("segment_id"),
        sa.UniqueConstraint("source_unit_id", "segment_order", name="uq_segment_order"),
    )
    op.create_table(
        "processing_runs",
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("schema_version_id", sa.String(length=36), nullable=False),
        sa.Column("source_unit_id", sa.String(length=36), nullable=False),
        sa.Column("pipeline_version", sa.String(length=50), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "running",
                "completed",
                "failed",
                name="runstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("llm_provider", sa.String(length=80), nullable=True),
        sa.Column("llm_model", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.ForeignKeyConstraint(
            ["schema_version_id"],
            ["schema_versions.schema_version_id"],
        ),
        sa.ForeignKeyConstraint(["source_unit_id"], ["source_units.source_unit_id"]),
        sa.PrimaryKeyConstraint("run_id"),
    )
    op.create_table(
        "extraction_executions",
        sa.Column("execution_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("dry_run", sa.Boolean(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "running",
                "succeeded",
                "failed",
                name="extractionexecutionstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("prompt_key", sa.String(length=120), nullable=False),
        sa.Column("prompt_version", sa.String(length=120), nullable=True),
        sa.Column("schema_name", sa.String(length=120), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=True),
        sa.Column("requested_llm_provider", sa.String(length=80), nullable=True),
        sa.Column("requested_llm_model", sa.String(length=120), nullable=True),
        sa.Column("resolved_llm_model", sa.String(length=120), nullable=True),
        sa.Column("segment_count", sa.Integer(), nullable=False),
        sa.Column("suggested_node_count", sa.Integer(), nullable=False),
        sa.Column("suggested_relation_count", sa.Integer(), nullable=False),
        sa.Column("created_candidate_node_count", sa.Integer(), nullable=False),
        sa.Column("created_candidate_relation_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("execution_id"),
    )
    op.create_table(
        "candidate_nodes",
        sa.Column("candidate_node_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("node_type", sa.String(length=80), nullable=False),
        sa.Column(
            "properties_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "merge_key_payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "evidence_refs_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "validated",
                "rejected",
                "review",
                "committed",
                name="candidatestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("candidate_node_id"),
    )
    op.create_table(
        "candidate_relations",
        sa.Column("candidate_relation_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("relation_type", sa.String(length=80), nullable=False),
        sa.Column("from_candidate_ref", sa.String(length=36), nullable=False),
        sa.Column("to_candidate_ref", sa.String(length=36), nullable=False),
        sa.Column(
            "properties_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column(
            "evidence_refs_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum(
                "pending",
                "validated",
                "rejected",
                "review",
                "committed",
                name="candidatestatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("candidate_relation_id"),
    )
    op.create_table(
        "validation_results",
        sa.Column("validation_result_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("candidate_ref", sa.String(length=36), nullable=False),
        sa.Column("rule_code", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("validation_result_id"),
    )
    op.create_table(
        "review_items",
        sa.Column("review_item_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("item_type", sa.String(length=50), nullable=False),
        sa.Column("item_ref", sa.String(length=36), nullable=False),
        sa.Column("reason_code", sa.String(length=120), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "open",
                "accepted",
                "rejected",
                "edited",
                name="reviewstatus",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("review_item_id"),
    )
    op.create_table(
        "graph_deltas",
        sa.Column("delta_id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=False),
        sa.Column("nodes_created", sa.Integer(), nullable=False),
        sa.Column("nodes_merged", sa.Integer(), nullable=False),
        sa.Column("relations_created", sa.Integer(), nullable=False),
        sa.Column("relations_merged", sa.Integer(), nullable=False),
        sa.Column("review_count", sa.Integer(), nullable=False),
        sa.Column("rejected_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.project_id"]),
        sa.ForeignKeyConstraint(["run_id"], ["processing_runs.run_id"]),
        sa.PrimaryKeyConstraint("delta_id"),
        sa.UniqueConstraint("run_id", name="uq_graph_delta_run"),
    )


def downgrade() -> None:
    op.drop_table("graph_deltas")
    op.drop_table("review_items")
    op.drop_table("validation_results")
    op.drop_table("candidate_relations")
    op.drop_table("candidate_nodes")
    op.drop_table("extraction_executions")
    op.drop_table("processing_runs")
    op.drop_table("segments")
    op.drop_table("source_units")
    op.drop_table("property_definitions")
    op.drop_table("relation_types")
    op.drop_table("node_types")
    op.drop_table("schema_versions")
    op.drop_table("structured_prompts")
    op.drop_table("projects")
