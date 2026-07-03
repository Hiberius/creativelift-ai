"""Postgres Row-Level Security on all organization-scoped data tables

Auth-layer tables (users, memberships, api_keys, user_sessions) and
organizations itself stay outside RLS: they are resolved before a tenant
is known. Every business-data table is FORCEd so even the table owner
cannot read across tenants without the `app.organization_id` GUC that
the API sets per transaction (see app/db/session.py).

Revision ID: 0004_row_level_security
Revises: 0003_human_login
Create Date: 2026-07-03
"""

from __future__ import annotations

from alembic import op

revision = "0004_row_level_security"
down_revision = "0003_human_login"
branch_labels = None
depends_on = None

TENANT_TABLES = (
    "approval_reviews",
    "approved_claims",
    "audit_logs",
    "bandit_arms",
    "bandits",
    "brand_packs",
    "briefs",
    "claim_evidence",
    "connectors",
    "creative_treatments",
    "creative_versions",
    "event_quality_snapshots",
    "events",
    "experiment_results",
    "experiment_variants",
    "experiments",
    "mmm_runs",
    "prompt_runs",
    "uplift_runs",
)


def upgrade() -> None:
    # The runtime connects as the non-superuser role creativelift_app
    # (created by the Postgres init script); superusers bypass RLS.
    op.execute(
        """
        DO $$ BEGIN
          IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'creativelift_app') THEN
            GRANT USAGE ON SCHEMA public TO creativelift_app;
            GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO creativelift_app;
            ALTER DEFAULT PRIVILEGES IN SCHEMA public
              GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO creativelift_app;
          END IF;
        END $$;
        """
    )
    for table in TENANT_TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(
            f"""
            CREATE POLICY tenant_isolation ON {table}
            USING (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid)
            WITH CHECK (organization_id = NULLIF(current_setting('app.organization_id', true), '')::uuid)
            """
        )


def downgrade() -> None:
    for table in TENANT_TABLES:
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation ON {table}")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
