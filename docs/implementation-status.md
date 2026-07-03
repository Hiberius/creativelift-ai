# Implementation Status

This is the honest current state of the MVP.

## Working And Tested

- FastAPI app imports and routes load.
- `/healthz`, `/readyz`, and `/metrics` exist.
- `/v1` route surface has no duplicate method/path registrations.
- Event ingestion validates identity requirements.
- Event ingestion supports idempotency behavior in tests.
- Event health summarizes totals, experiment coverage, variant coverage, revenue coverage, quality score, and warnings.
- Measurement functions compute lift, confidence interval, p-value, SRM, CUPED adjustment, and event-derived experiment results.
- Experiment insights turn result recommendations into decision summaries, evidence, and next steps.
- Bandit service implements Bernoulli Thompson Sampling.
- Uplift service has a segment-level baseline.
- MMM service has a demo contribution model.
- Connector adapters have contract tests.
- Product workflow API coverage covers workspace setup, API keys, Creative Treatment review, experiment lifecycle, connector registry, and the repository boundary.
- Python and TypeScript SDK ingestion, assignment, event health, and insight helpers are covered by lightweight tests.
- Browser and server-side SDK tracking examples exist under `examples/sdk-tracking`.
- Database runtime and Alembic metadata are aligned on the SQLAlchemy schema source.
- Connector database columns are aligned with the active API contract (`provider`, `display_name`).
- Claim evidence database table is aligned with the active claim evidence API contract.
- Modular resource tables are aligned with active prompt-run, MMM-run, uplift-run, and connector API contracts.
- A lazy SQLAlchemy repository implementation exists for modular resources, while the default runtime remains in-memory demo mode.
- A core repository boundary covers organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events with memory and lazy SQLAlchemy backends.
- `/v1/demo/analyze` accepts manual control/treatment observations and returns lift, confidence, SRM, sample-size planning, and a recommendation.
- `/v1/demo/reports` saves, lists, clears, persists, and exports local measurement decision reports for the no-dependency lab.
- `/v1/demo/reports/import` parses wide CSV rows into saved measurement decision reports with row-level validation errors.
- `/v1/demo/reports/summary` aggregates saved measurement reports into winner/loser counts, average lift, and best report.
- One-click demo scenario creates a workspace, approved Creative Treatments, experiment traffic, measured result, event health, and decision insight.
- `/demo` serves a no-dependency local measurement lab with analysis, CSV upload/paste import, persistent saved reports, portfolio summary, CSV/JSON/Markdown export, copied JSON, and scenario generation directly from FastAPI.
- Frontend route inventory test runs without installing dependencies.
- Frontend has a shared API client for local FastAPI calls.
- `/app/api-keys` can list, create, and delete API keys against the API.
- `/app/briefs` can load briefs from the API with a demo fallback.
- `/app/briefs/new` can create briefs and call the mock variant generator.
- Generated variants can be saved as Creative Treatments from `/app/briefs/new`.
- `/app/approvals` can load Creative Treatments and approve/reject them.
- `/app/approvals` can attach claim evidence URLs during approval.
- `/app/experiments` can list, create, start, pause, and complete experiments.
- `/app/experiments/[id]` can load experiment detail and trigger status actions.
- `/app/experiments/[id]` can preview deterministic unit assignment for an experiment.
- Experiment start validates control/treatment structure and approved Creative Treatments.
- Experiment start blocks approved Creative Treatments that still need claim evidence.
- `/app/experiments/[id]/results` can load event-derived result data and decision insights from the API with demo fallbacks.
- `/app/creatives` can load Creative Treatments from the API with a demo fallback.
- `/app/creatives/[id]` can load a Creative Treatment lineage view from the API with a demo fallback.
- `/app/dashboard` can launch the one-click demo scenario and load measurement summary cards, approval risk, event health, and lineage audit entries from the API with demo fallbacks.
- `/app/events` can send a demo ingestion event to `/v1/events/ingest`.
- `/app/events` can list recent demo events from `GET /v1/events`.
- `/app/events` can load event health from `GET /v1/events/health`.
- `/app/connectors` can list and create connector registry records against the API with a demo fallback.
- `/app/onboarding` can create an organization and brand pack against the API.
- `/app/settings` can load the current organization/principal and brand packs from the API.
- `/app/settings` can show recent audit log entries from the API.
- `/app/settings` can list and create claim evidence records from the API.

- The SQLAlchemy core/resource repositories are exercised by tests on in-memory SQLite (`pytest -m sqlalchemy`): repository parity (idempotency, API key hashing, tenancy), modular resources, and an end-to-end API workflow through the real routes.
- Alembic migrations (`0001` + `0002`) execute against a disposable Postgres with upgrade/downgrade/re-upgrade verified (`make migration-smoke`, CI `migrations` job).
- Event quality snapshots persist per accepted ingest (`event_quality_snapshots`, migration `0002`) and are served by `GET /v1/events/health/history` on both backends.
- `GET /v1/measurement/summary` is computed from repository aggregations (events, running experiments, approval counts) with the demo cards preserved as the zero-event fallback.
- Docker Compose runs the persistent profile: `RESOURCE_REPOSITORY_BACKEND=sqlalchemy` plus `alembic upgrade head` on API boot.
- `/readyz` performs a real database ping under the sqlalchemy profile (503 when unreachable).
- Approval risk and lineage dashboard panels already read from repository-backed routes (`/v1/creative-treatments`, `/v1/audit-logs`); no demo-only aggregation remains on those paths.
- API keys authenticate against the repository via HMAC hash lookup on both auth schemes; scopes are enforced on ingestion; revocation is immediate.
- Production mode rejects anonymous/demo credentials and refuses to boot with development secrets.
- Security headers middleware and demo-console CSP are active on every response.
- The OpenAI-compatible generator provider performs real chat/completions calls with structured-variant parsing and lineage capture (mock stays the default).
- The Next.js production build compiles (Next 15 async params fixed) and 7 Playwright E2E journeys pass against the production build plus a live Postgres-backed API (`make e2e`).
- The API imports its statistics from services/experiment-engine (single source); the router's bandit decisions run through services/bandit-service.
- Sequential testing is real: always-valid mSPRT (`sequential_peek`), exposed as an additive `sequential` block in `/v1/demo/analyze` and experiment results.
- `POST /v1/measurement/mmm-runs` and `uplift-runs` compute synchronously via their services with populated outputs and clean failure states.
- All 7 connector adapters implement `validate_config()`; PostHog implements `pull()` with cursor pagination (tested against mocked transports); `POST /v1/connectors/{id}/sync` ingests via push (any provider) or pull (PostHog) with idempotent replay.
- The frontend never lies: fallback data is labeled with a "Demo data" badge and API failures show a human-readable banner with Retry; skeleton loaders cover the summary grid and detail panels.
- Human login works end to end: register/login/logout with scrypt-hashed passwords and revocable DB-backed sessions; the dashboard has a `/login` page, session-aware header, and auto-redirect when the API requires auth (E2E covered).
- RBAC is enforced: approvals need owner/admin/marketer, API-key management needs owner/admin, service keys cannot approve creatives.
- Postgres Row-Level Security isolates tenants at the database: FORCEd policies on all 19 organization-scoped tables, per-transaction tenant GUC, non-superuser runtime role; verified by the migration smoke test.
- Rate limiting can run on Redis (compose default) with in-memory fallback; ingest-time quality snapshots use SQL aggregates instead of full scans.
- The compose stack ships a daily database backup sidecar with 14-day retention.

Current lightweight verification:

```text
python3 -m compileall -q apps/api services connectors packages/sdk-python examples
python3 -m pytest  # 89 tests (+2 skipped without a migration database)
npm --workspace apps/web run test  # 5 tests
python3 -m pytest -m sqlalchemy  # SQLAlchemy backend on SQLite
make migration-smoke  # Alembic roundtrip on disposable Postgres
```

## Implemented As Demo/In-Memory

- API routes use demo stores for local behavior outside the Docker/sqlalchemy profile.
- Organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and event ingestion use the CoreRepository boundary; memory remains the bare-metal default, sqlalchemy is the Docker profile.
- Experiment result endpoint aggregates matching repository events and returns deterministic demo output when no matching events exist.
- Experiment insight endpoint uses repository/demo result data until persistent analytics storage exists.
- Measurement decision reports are persisted to an ignored local JSON file until the report repository is promoted to database-backed storage.
- API key lifecycle has memory and lazy SQLAlchemy repository implementations.
- Audit log has memory and lazy SQLAlchemy repository implementations.
- Brand pack, brief, Creative Treatment, experiment, bandit, demo measurement run, and claim evidence registries have memory and lazy SQLAlchemy repository implementations.
- Event ingestion has memory and lazy SQLAlchemy repository implementations.
- Event health is computed from repository events.
- Connector registry route returns demo/in-memory values.

## Scaffolded

- Postgres-backed production hardening (RLS, pooling, backups) beyond the tested repository layer.
- OIDC/SSO providers on top of the local email+password login.
- Background workers.
- ClickHouse event store.
- Scheduled/continuous connector sync (PostHog pull and push-mode sync exist; Rudder/Snowplow live pull and schedulers do not).
- Live Google Ads and Meta Ads sync.
- Live HubSpot sync.
- OpenAI-compatible provider implementation.
- Contextual bandits.
- EconML/CausalML uplift adapters.
- PyMC-Marketing/Meridian/Robyn MMM adapters.

## Not Verified In This Environment

These require dependency installation, Docker, network, or heavier local execution:

- Docker Compose runtime (config updated for the sqlalchemy profile; full `docker compose up` still needs a machine with Docker).
- OpenAPI schema snapshot in CI.
- End-to-end browser tests.

## P0: Next Engineering Tasks

1. ~~Add Alembic migration smoke test against disposable Postgres.~~ Done (`make migration-smoke`).
2. ~~Move approval, lineage, and dashboard aggregations fully onto repository-backed reads.~~ Done (`measurement_summary_stats`; approval/lineage panels already read repository routes).
3. ~~Enable SQLAlchemy repository mode in a documented local profile.~~ Done (Docker profile + docs/self-hosting.md storage profiles).
4. ~~Add persistent event quality trend storage.~~ Done (`event_quality_snapshots` + `GET /v1/events/health/history`).
5. ~~Add browser E2E once dependencies are intentionally installed.~~ Done (`make e2e`, 7 Playwright journeys).
6. ~~Add real auth provider~~ Done: hashed API keys with scopes and production guards, local email+password login with revocable sessions, RBAC, and Postgres RLS. Still open: OIDC/SSO providers.
7. Add persistent audit/event views for operators.
8. ~~Replace per-ingest O(N) event quality snapshot recomputation with a SQL rollup.~~ Done (`compute_event_health` aggregates).

## P1: Product Depth

1. Data quality trend dashboard.
2. Enforce evidence references against persisted registry records once SQLAlchemy backend is the default.
3. Persist creative insight records from winners.
4. Warehouse export scaffold.
5. Connector scheduling model.
6. RBAC enforcement beyond role scaffolds.
7. RLS policy migration.
8. Browser E2E test once dependencies are intentionally installed.

## P2: Launch Polish

1. Real screenshots generated from running app.
2. Product Hunt style demo script.
3. Seed blog posts expanded from outlines.
4. GitHub repo topics and issue labels applied.
5. First release notes for `v0.1.0 "Prompt to Profit"`.
