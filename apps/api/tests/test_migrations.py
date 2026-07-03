"""Alembic migration smoke tests against a disposable Postgres database.

Run locally with `make migration-smoke` (starts the compose Postgres) or set
CREATIVELIFT_MIGRATION_TEST_DATABASE_URL to any reachable Postgres server.
Each test creates and drops its own database, so the compose data volume is
never touched.
"""

from __future__ import annotations

import os
import subprocess
import sys
import uuid
from pathlib import Path

import pytest

MIGRATION_TEST_DATABASE_URL = os.getenv("CREATIVELIFT_MIGRATION_TEST_DATABASE_URL")
API_DIR = Path(__file__).resolve().parents[1]
HEAD_REVISION = "0004_row_level_security"

pytestmark = [
    pytest.mark.migration,
    pytest.mark.skipif(
        not MIGRATION_TEST_DATABASE_URL,
        reason="set CREATIVELIFT_MIGRATION_TEST_DATABASE_URL to run migration smoke tests",
    ),
]


def _run_alembic(arguments: list[str], database_url: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", *arguments],
        cwd=API_DIR,
        env={**os.environ, "DATABASE_URL": database_url},
        check=True,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def disposable_database():
    sqlalchemy = pytest.importorskip("sqlalchemy")
    from sqlalchemy.engine import make_url

    admin_url = make_url(MIGRATION_TEST_DATABASE_URL)
    database_name = f"creativelift_mig_{uuid.uuid4().hex[:10]}"
    admin_engine = sqlalchemy.create_engine(
        admin_url.set(database="postgres"), isolation_level="AUTOCOMMIT"
    )
    with admin_engine.connect() as connection:
        connection.execute(sqlalchemy.text(f'CREATE DATABASE "{database_name}"'))
    try:
        yield str(admin_url.set(database=database_name))
    finally:
        with admin_engine.connect() as connection:
            connection.execute(
                sqlalchemy.text(f'DROP DATABASE IF EXISTS "{database_name}" WITH (FORCE)')
            )
        admin_engine.dispose()


def _inspect(database_url: str):
    import sqlalchemy

    engine = sqlalchemy.create_engine(database_url)
    try:
        inspector = sqlalchemy.inspect(engine)
        tables = set(inspector.get_table_names())
        version = None
        if "alembic_version" in tables:
            with engine.connect() as connection:
                version = connection.scalar(
                    sqlalchemy.text("SELECT version_num FROM alembic_version")
                )
        event_constraints = (
            {item["name"] for item in inspector.get_unique_constraints("events")}
            if "events" in tables
            else set()
        )
        snapshot_indexes = (
            {item["name"] for item in inspector.get_indexes("event_quality_snapshots")}
            if "event_quality_snapshots" in tables
            else set()
        )
        return tables, version, event_constraints, snapshot_indexes
    finally:
        engine.dispose()


def test_alembic_upgrade_head_creates_full_schema(disposable_database):
    _run_alembic(["upgrade", "head"], disposable_database)

    tables, version, event_constraints, snapshot_indexes = _inspect(disposable_database)

    expected_tables = {
        "organizations",
        "users",
        "memberships",
        "api_keys",
        "brand_packs",
        "approved_claims",
        "claim_evidence",
        "briefs",
        "creative_treatments",
        "creative_versions",
        "prompt_runs",
        "approval_reviews",
        "experiments",
        "experiment_variants",
        "events",
        "experiment_results",
        "bandits",
        "bandit_arms",
        "mmm_runs",
        "uplift_runs",
        "connectors",
        "audit_logs",
        "event_quality_snapshots",
        "user_sessions",
    }
    assert expected_tables <= tables
    assert version == HEAD_REVISION
    assert "uq_events_org_idempotency" in event_constraints
    assert "ix_event_quality_snapshots_org_captured" in snapshot_indexes


def test_row_level_security_isolates_tenants(disposable_database):
    """RLS must block cross-tenant reads even for the table owner (FORCE)."""
    import sqlalchemy

    from sqlalchemy.engine import make_url

    admin_engine = sqlalchemy.create_engine(disposable_database, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DO $$ BEGIN
                  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'creativelift_app') THEN
                    CREATE ROLE creativelift_app LOGIN PASSWORD 'creativelift_app_dev';
                  END IF;
                END $$;
                """
            )
        )
    admin_engine.dispose()

    _run_alembic(["upgrade", "head"], disposable_database)
    app_url = make_url(disposable_database).set(
        username="creativelift_app", password="creativelift_app_dev"
    )
    engine = sqlalchemy.create_engine(app_url)
    admin = sqlalchemy.create_engine(disposable_database)
    org_a, org_b = str(uuid.uuid4()), str(uuid.uuid4())
    try:
        with admin.begin() as connection:
            for org_id, slug in ((org_a, "org-a"), (org_b, "org-b")):
                connection.execute(
                    sqlalchemy.text(
                        "INSERT INTO organizations (id, name, slug) VALUES (:id, :name, :slug)"
                    ),
                    {"id": org_id, "name": slug, "slug": slug},
                )

        def _insert_brief(org_id: str, name: str) -> None:
            with engine.begin() as connection:
                connection.execute(
                    sqlalchemy.text("SELECT set_config('app.organization_id', :org, true)"),
                    {"org": org_id},
                )
                connection.execute(
                    sqlalchemy.text(
                        "INSERT INTO briefs (id, organization_id, name, objective, target_audience, channel, primary_kpi)"
                        " VALUES (:id, :org, :name, 'obj', 'aud', 'email', 'signup')"
                    ),
                    {"id": str(uuid.uuid4()), "org": org_id, "name": name},
                )

        _insert_brief(org_a, "brief-a")
        _insert_brief(org_b, "brief-b")

        def _count_briefs(org_id: str | None) -> int:
            with engine.begin() as connection:
                if org_id is not None:
                    connection.execute(
                        sqlalchemy.text("SELECT set_config('app.organization_id', :org, true)"),
                        {"org": org_id},
                    )
                return connection.scalar(sqlalchemy.text("SELECT count(*) FROM briefs"))

        assert _count_briefs(org_a) == 1
        assert _count_briefs(org_b) == 1
        assert _count_briefs(None) == 0, "without a tenant GUC the owner must see nothing"

        with engine.begin() as connection:
            connection.execute(
                sqlalchemy.text("SELECT set_config('app.organization_id', :org, true)"),
                {"org": org_a},
            )
            names = connection.execute(sqlalchemy.text("SELECT name FROM briefs")).scalars().all()
        assert names == ["brief-a"], "tenant A must never see tenant B rows"
    finally:
        engine.dispose()
        admin.dispose()


def test_alembic_downgrade_base_and_reupgrade_roundtrip(disposable_database):
    _run_alembic(["upgrade", "head"], disposable_database)
    _run_alembic(["downgrade", "base"], disposable_database)

    tables, _version, _constraints, _indexes = _inspect(disposable_database)
    assert "organizations" not in tables
    assert "event_quality_snapshots" not in tables

    _run_alembic(["upgrade", "head"], disposable_database)
    tables, version, _constraints, _indexes = _inspect(disposable_database)
    assert "event_quality_snapshots" in tables
    assert version == HEAD_REVISION
