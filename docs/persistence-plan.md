# Persistence Plan

The API uses in-memory demo stores by default so the product can run locally without Postgres, and the Docker profile now runs the SQLAlchemy backend against Postgres with migrations applied on boot. The repository boundary is explicit, which lets us replace storage route by route without changing routers or frontend contracts.

## Current State

- Active route schemas live in `apps/api/app/schemas/common.py` for core app routes and `apps/api/app/schemas/domain.py` for modular resource routes.
- Modular resources use `ResourceService`, backed by the `ResourceRepository` protocol in `apps/api/app/services/repositories.py`.
- Organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events use `CoreRepository` in `apps/api/app/services/core_repositories.py`.
- `InMemoryResourceRepository` is the default implementation.
- `SQLAlchemyResourceRepository` is available for modular resources, but is not yet the default runtime.
- `InMemoryCoreRepository` is the default implementation for organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events.
- `SQLAlchemyCoreRepository` is available for organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events, but is not yet the default runtime.
- `RESOURCE_REPOSITORY_BACKEND=memory` keeps local demo mode light; `sqlalchemy` selects SQLAlchemy implementations when dependencies and database are intentionally available.
- `docker compose up` runs the `sqlalchemy` profile: `alembic upgrade head` on boot, Postgres-backed persistence, reset via `docker compose down -v`.
- `core_repository` is a `CoreRepositoryProxy`: tests and profiles swap the delegate with `use()`/`reset()` without touching routers.
- The SQLAlchemy backend is exercised by tests on in-memory SQLite (`pytest -m sqlalchemy`): repository parity, idempotency, API key hashing, modular resources, and an end-to-end API workflow.
- Alembic migrations are smoke-tested against a disposable Postgres (`make migration-smoke`): upgrade head, downgrade base, re-upgrade.
- Event quality snapshots persist per ingest in `event_quality_snapshots` (migration `0002`) and are served by `GET /v1/events/health/history`. Snapshot capture recomputes health from all events (O(N) per ingest): replace with a SQL rollup before high-volume production use.
- `GET /v1/measurement/summary` aggregates from the repository (`measurement_summary_stats`) and falls back to demo cards only when the organization has no events.
- `apps/api/app/db/models.py` contains the Postgres-first SQLAlchemy schema used by Alembic and `app/db/session.py`.
- The older SQLModel scaffold has been removed to avoid two competing model sources.

## Migration Order

1. ~~Smoke-test `RESOURCE_REPOSITORY_BACKEND=sqlalchemy` only when dependencies and a disposable database are intentionally available.~~ Done: `make migration-smoke` + `pytest -m sqlalchemy`.
2. Move modular routes first: connectors, prompt runs, measurement run resources. (SQLAlchemy implementations now covered by tests; memory remains the bare-metal default.)
3. ~~Add repository-level tests with SQLite only where JSON/UUID behavior matches Postgres.~~ Done: JSONB columns use a JSON variant on non-Postgres dialects.
4. ~~Add Postgres smoke tests only when Docker or a disposable database is intentionally approved.~~ Done: disposable-database Alembic roundtrip in `apps/api/tests/test_migrations.py`.

## Guardrails

- Do not change API response shapes while swapping repositories.
- Do not introduce a second ORM model source for the same table.
- Keep demo fallback behavior in the frontend until persistent local setup is documented.
- Keep API key hashing and event idempotency covered by tests before moving them to Postgres.
