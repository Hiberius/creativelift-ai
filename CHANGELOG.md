# Changelog

## v0.1.0 "Prompt to Profit" — 2026-07-02

- Enabled the SQLAlchemy repository backend as the documented Docker profile: compose now sets `RESOURCE_REPOSITORY_BACKEND=sqlalchemy` and runs `alembic upgrade head` on API boot, so data persists across restarts (`docker compose down -v` resets).
- Added persistent event quality trend storage: `event_quality_snapshots` table (migration `0002`), snapshots captured on every accepted ingest and demo scenario, exposed via `GET /v1/events/health/history`.
- Moved `GET /v1/measurement/summary` onto repository-backed aggregations (events, experiments, approvals) with the deterministic demo cards preserved as the zero-event fallback.
- Added Alembic migration smoke tests against a disposable Postgres (`make migration-smoke`, CI `migrations` job) covering upgrade, downgrade, and re-upgrade.
- Added SQLAlchemy backend tests on in-memory SQLite: repository parity (idempotency, API key hashing, tenancy), modular resource repository coverage, and an end-to-end API workflow (`make test-sqlalchemy`).
- Added `CoreRepositoryProxy` so tests and runtime profiles can swap repository backends without touching routers.
- Fixed the SQLAlchemy model layer failing to import (`AuditLog.metadata` clashed with the Declarative API reserved name; DB column unchanged).
- Made JSONB columns portable: JSONB on Postgres, generic JSON on other dialects (enables SQLite-backed tests).
- Hardened event ingestion on SQLAlchemy against concurrent idempotency-key replays using the existing unique constraint.
- `/readyz` now performs a real database ping under the sqlalchemy profile and returns 503 when the database is unreachable.
- The demo principal pointer is restored from the latest persisted organization on API boot under the sqlalchemy profile, so dashboards keep showing data after restarts until real auth lands.
- Wired core app screens to API clients with demo fallbacks.
- Added Events ingestion UI, connector registry UI, onboarding/settings managers, and experiment detail manager.
- Added repository boundary for modular resources.
- Aligned database runtime and Alembic metadata on the SQLAlchemy schema source.
- Removed the unused SQLModel scaffold.
- Aligned connector database columns with the active API contract.
- Added a lazy SQLAlchemy resource repository for modular resources.
- Added `RESOURCE_REPOSITORY_BACKEND` to select memory or SQLAlchemy repositories.
- Added recent event listing API and Events UI table.
- Added event health API, SDK helpers, and Events UI quality panel.
- Wired dashboard ingestion health to the event health API.
- Wired dashboard approval risk and lineage panels to API data.
- Added audit log API wiring to Settings.
- Added claim evidence registry API and Settings UI.
- Added claim evidence URL attachment to the approval queue.
- Added deterministic experiment assignment endpoint and UI preview.
- Added event-derived experiment result aggregation with demo fallback.
- Added experiment insight API, result page panel, and SDK helpers.
- Added experiment launch validation for control/treatment structure and approved Creative Treatments.
- Added claim-evidence-aware launch blocking for governed Creative Treatments.
- Added CoreRepository boundary for organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events with memory and lazy SQLAlchemy backends.
- Added one-click demo scenario API and dashboard launcher for an end-to-end measured creative test.
- Added FastAPI-served `/demo` console for a no-dependency local product demo.
- Upgraded `/demo` into a local measurement lab with manual experiment analysis via `POST /v1/demo/analyze`.
- Added local measurement decision reports via `POST /v1/demo/reports` and `GET /v1/demo/reports`.
- Added CSV import for local measurement reports via `POST /v1/demo/reports/import`.
- Added file-backed persistence plus CSV, JSON, and Markdown export for local measurement reports.
- Added local report portfolio summary for winner/loser counts, average lift, and best report.
- Added experiment assignment helpers to the TypeScript and Python SDKs.
- Added browser and server-side SDK tracking examples.
- Aligned SDK ingestion headers on `X-API-Key`.
- Added API reference drift test and product workflow API tests.

## v0.1.0 "Prompt to Profit"

- Initial MVP repository for CreativeLift AI.
- FastAPI backend, Next.js web app, measurement services, connector scaffolds, docs, Docker Compose, and CI.
