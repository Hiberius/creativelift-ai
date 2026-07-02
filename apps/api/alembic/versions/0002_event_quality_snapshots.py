"""event quality snapshots for persistent trend storage

Revision ID: 0002_event_quality_snapshots
Revises: 0001_initial_schema
Create Date: 2026-07-02
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_event_quality_snapshots"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True)


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def org_fk(nullable: bool = False) -> sa.Column:
    return sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=nullable)


def upgrade() -> None:
    op.create_table(
        "event_quality_snapshots",
        uuid_pk(),
        org_fk(),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unique_actors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("events_with_experiment", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("events_with_variant", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("conversion_events", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("revenue", sa.Numeric(14, 2), nullable=False, server_default="0"),
        sa.Column("experiment_coverage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("variant_coverage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("revenue_coverage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("warnings", postgresql.JSONB(), nullable=False, server_default="[]"),
        *timestamps(),
    )
    op.create_index(
        "ix_event_quality_snapshots_org_captured",
        "event_quality_snapshots",
        ["organization_id", "captured_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_event_quality_snapshots_org_captured", table_name="event_quality_snapshots")
    op.drop_table("event_quality_snapshots")
