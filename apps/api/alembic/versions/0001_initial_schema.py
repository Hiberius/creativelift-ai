"""initial CreativeLift AI schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
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
        "organizations",
        uuid_pk(),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("plan", sa.String(40), nullable=False, server_default="open_source"),
        sa.Column("settings", postgresql.JSONB(), nullable=False, server_default="{}"),
        *timestamps(),
    )
    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("auth_provider", sa.String(80), nullable=False, server_default="local"),
        sa.Column("external_subject", sa.String(240), nullable=True),
        *timestamps(),
    )
    op.create_table("memberships", uuid_pk(), org_fk(), sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False), sa.Column("role", sa.String(40), nullable=False), *timestamps())
    op.create_unique_constraint("uq_membership_org_user", "memberships", ["organization_id", "user_id"])
    op.create_table("api_keys", uuid_pk(), org_fk(), sa.Column("name", sa.String(160), nullable=False), sa.Column("prefix", sa.String(24), nullable=False), sa.Column("hashed_key", sa.String(128), nullable=False), sa.Column("scopes", postgresql.JSONB(), nullable=False, server_default="[]"), sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True), sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True), *timestamps())
    op.create_index("ix_api_keys_org_prefix", "api_keys", ["organization_id", "prefix"])
    op.create_table("brand_packs", uuid_pk(), org_fk(), sa.Column("name", sa.String(160), nullable=False), sa.Column("voice", sa.Text(), nullable=False, server_default=""), sa.Column("guardrails", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("prohibited_claims", postgresql.JSONB(), nullable=False, server_default="[]"), sa.Column("regulated_category", sa.Boolean(), nullable=False, server_default=sa.false()), *timestamps())
    op.create_table("approved_claims", uuid_pk(), org_fk(), sa.Column("brand_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("brand_packs.id"), nullable=False), sa.Column("claim", sa.Text(), nullable=False), sa.Column("evidence_url", sa.Text(), nullable=True), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True), *timestamps())
    op.create_table("claim_evidence", uuid_pk(), org_fk(), sa.Column("brand_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("brand_packs.id"), nullable=True), sa.Column("claim", sa.Text(), nullable=False), sa.Column("evidence_url", sa.Text(), nullable=False), sa.Column("source_name", sa.String(180), nullable=False, server_default=""), sa.Column("notes", sa.Text(), nullable=False, server_default=""), sa.Column("status", sa.String(40), nullable=False, server_default="approved"), *timestamps())
    op.create_index("ix_claim_evidence_org_status", "claim_evidence", ["organization_id", "status"])
    op.create_table("briefs", uuid_pk(), org_fk(), sa.Column("brand_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("brand_packs.id"), nullable=True), sa.Column("name", sa.String(180), nullable=False), sa.Column("objective", sa.String(180), nullable=False), sa.Column("target_audience", sa.Text(), nullable=False), sa.Column("channel", sa.String(80), nullable=False), sa.Column("primary_kpi", sa.String(80), nullable=False), sa.Column("status", sa.String(40), nullable=False, server_default="draft"), sa.Column("body", sa.Text(), nullable=False, server_default=""), *timestamps())
    op.create_index("ix_briefs_org_status", "briefs", ["organization_id", "status"])
    op.create_table("creative_treatments", uuid_pk(), org_fk(), sa.Column("brief_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("briefs.id"), nullable=True), sa.Column("brand_pack_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("brand_packs.id"), nullable=True), sa.Column("name", sa.String(180), nullable=False), sa.Column("objective", sa.String(180), nullable=False), sa.Column("target_audience", sa.Text(), nullable=False), sa.Column("channel", sa.String(80), nullable=False), sa.Column("placement", sa.String(120), nullable=False, server_default=""), sa.Column("angle", sa.String(160), nullable=False, server_default=""), sa.Column("hook", sa.Text(), nullable=False, server_default=""), sa.Column("cta", sa.String(120), nullable=False, server_default=""), sa.Column("offer", sa.String(180), nullable=False, server_default=""), sa.Column("copy", sa.Text(), nullable=False, server_default=""), sa.Column("media_metadata", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("human_edited", sa.Boolean(), nullable=False, server_default=sa.false()), sa.Column("compliance_status", sa.String(40), nullable=False, server_default="pending_review"), sa.Column("approval_status", sa.String(40), nullable=False, server_default="draft"), sa.Column("approved_claim_ids", postgresql.JSONB(), nullable=False, server_default="[]"), sa.Column("metrics_snapshot", postgresql.JSONB(), nullable=False, server_default="{}"), *timestamps())
    op.create_index("ix_treatments_org_status", "creative_treatments", ["organization_id", "approval_status"])
    op.create_index("ix_treatments_org_channel", "creative_treatments", ["organization_id", "channel"])
    op.create_table("creative_versions", uuid_pk(), org_fk(), sa.Column("creative_treatment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("creative_treatments.id"), nullable=False), sa.Column("version", sa.Integer(), nullable=False), sa.Column("snapshot", postgresql.JSONB(), nullable=False), sa.Column("edited_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True), sa.Column("change_note", sa.Text(), nullable=False, server_default=""), *timestamps())
    op.create_table("prompt_runs", uuid_pk(), org_fk(), sa.Column("brief_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("briefs.id"), nullable=True), sa.Column("provider", sa.String(80), nullable=False), sa.Column("model", sa.String(120), nullable=False), sa.Column("prompt", sa.Text(), nullable=False), sa.Column("variables", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("response", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("status", sa.String(40), nullable=False, server_default="succeeded"), sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"), sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"), *timestamps())
    op.create_index("ix_prompt_runs_brief", "prompt_runs", ["brief_id"])
    op.create_table("approval_reviews", uuid_pk(), org_fk(), sa.Column("creative_treatment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("creative_treatments.id"), nullable=False), sa.Column("reviewer_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True), sa.Column("status", sa.String(40), nullable=False), sa.Column("notes", sa.Text(), nullable=False, server_default=""), sa.Column("claim_evidence_urls", postgresql.JSONB(), nullable=False, server_default="[]"), *timestamps())
    op.create_table("experiments", uuid_pk(), org_fk(), sa.Column("name", sa.String(180), nullable=False), sa.Column("hypothesis", sa.Text(), nullable=False), sa.Column("primary_metric", sa.String(80), nullable=False), sa.Column("guardrail_metric", sa.String(80), nullable=True), sa.Column("randomization_unit", sa.String(80), nullable=False, server_default="anonymous_id"), sa.Column("status", sa.String(40), nullable=False, server_default="draft"), sa.Column("channel", sa.String(80), nullable=False, server_default=""), sa.Column("decision_rule", sa.Text(), nullable=False, server_default=""), sa.Column("minimum_detectable_effect", sa.Float(), nullable=True), sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True), sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True), sa.Column("notes", sa.Text(), nullable=False, server_default=""), *timestamps())
    op.create_index("ix_experiments_org_status", "experiments", ["organization_id", "status"])
    op.create_table("experiment_variants", uuid_pk(), org_fk(), sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=False), sa.Column("creative_treatment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("creative_treatments.id"), nullable=True), sa.Column("key", sa.String(80), nullable=False), sa.Column("allocation", sa.Float(), nullable=False), sa.Column("is_control", sa.Boolean(), nullable=False, server_default=sa.false()), *timestamps())
    op.create_unique_constraint("uq_experiment_variant_key", "experiment_variants", ["experiment_id", "key"])
    op.create_table("events", uuid_pk(), org_fk(), sa.Column("event_name", sa.String(80), nullable=False), sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False), sa.Column("anonymous_id", sa.String(180), nullable=True), sa.Column("user_id", sa.String(180), nullable=True), sa.Column("creative_treatment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("creative_treatments.id"), nullable=False), sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=True), sa.Column("variant_id", sa.String(120), nullable=True), sa.Column("channel", sa.String(80), nullable=True), sa.Column("placement", sa.String(120), nullable=True), sa.Column("value", sa.Numeric(12, 2), nullable=True), sa.Column("currency", sa.String(3), nullable=True), sa.Column("idempotency_key", sa.String(180), nullable=True), sa.Column("properties", postgresql.JSONB(), nullable=False, server_default="{}"), *timestamps())
    op.create_index("ix_events_org_time", "events", ["organization_id", "timestamp"])
    op.create_index("ix_events_treatment", "events", ["creative_treatment_id"])
    op.create_index("ix_events_experiment_variant", "events", ["experiment_id", "variant_id"])
    op.create_unique_constraint("uq_events_org_idempotency", "events", ["organization_id", "idempotency_key"])
    op.create_table("experiment_results", uuid_pk(), org_fk(), sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=False), sa.Column("result", postgresql.JSONB(), nullable=False), sa.Column("recommendation", sa.String(40), nullable=False), *timestamps())
    op.create_table("bandits", uuid_pk(), org_fk(), sa.Column("name", sa.String(180), nullable=False), sa.Column("policy", sa.String(80), nullable=False, server_default="thompson_sampling"), sa.Column("status", sa.String(40), nullable=False, server_default="draft"), *timestamps())
    op.create_table("bandit_arms", uuid_pk(), org_fk(), sa.Column("bandit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("bandits.id"), nullable=False), sa.Column("creative_treatment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("creative_treatments.id"), nullable=True), sa.Column("name", sa.String(160), nullable=False), sa.Column("alpha", sa.Float(), nullable=False, server_default="1"), sa.Column("beta", sa.Float(), nullable=False, server_default="1"), *timestamps())
    op.create_table("mmm_runs", uuid_pk(), org_fk(), sa.Column("name", sa.String(200), nullable=False), sa.Column("status", sa.String(40), nullable=False, server_default="queued"), sa.Column("date_start", sa.DateTime(timezone=True), nullable=True), sa.Column("date_end", sa.DateTime(timezone=True), nullable=True), sa.Column("inputs", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("outputs", postgresql.JSONB(), nullable=False, server_default="{}"), *timestamps())
    op.create_table("uplift_runs", uuid_pk(), org_fk(), sa.Column("name", sa.String(200), nullable=False), sa.Column("experiment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("experiments.id"), nullable=True), sa.Column("status", sa.String(40), nullable=False, server_default="queued"), sa.Column("inputs", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("outputs", postgresql.JSONB(), nullable=False, server_default="{}"), *timestamps())
    op.create_table("connectors", uuid_pk(), org_fk(), sa.Column("provider", sa.String(120), nullable=False), sa.Column("display_name", sa.String(200), nullable=False), sa.Column("status", sa.String(40), nullable=False, server_default="disconnected"), sa.Column("config", postgresql.JSONB(), nullable=False, server_default="{}"), sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True), *timestamps())
    op.create_table("audit_logs", uuid_pk(), org_fk(), sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True), sa.Column("action", sa.String(120), nullable=False), sa.Column("target_type", sa.String(120), nullable=False), sa.Column("target_id", sa.String(120), nullable=True), sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"), *timestamps())
    op.create_index("ix_audit_org_time", "audit_logs", ["organization_id", "created_at"])


def downgrade() -> None:
    for table in [
        "audit_logs",
        "connectors",
        "uplift_runs",
        "mmm_runs",
        "bandit_arms",
        "bandits",
        "experiment_results",
        "events",
        "experiment_variants",
        "experiments",
        "approval_reviews",
        "prompt_runs",
        "creative_versions",
        "creative_treatments",
        "briefs",
        "claim_evidence",
        "approved_claims",
        "brand_packs",
        "api_keys",
        "memberships",
        "users",
        "organizations",
    ]:
        op.drop_table(table)
