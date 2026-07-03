# Changelog

## Unreleased — human login, RBAC, and tenant isolation at the database

- Human login: email + password registration and sign-in (`/v1/auth/register`, `/v1/auth/login`, `/v1/auth/logout`, `/v1/auth/session`) with stdlib scrypt password hashing and revocable server-side sessions (httpOnly cookie). Migration `0003` adds `users.hashed_password` and the `user_sessions` table.
- Role-based access control: approvals require owner/admin/marketer, API-key management requires owner/admin, experiment lifecycle allows service keys; enforced on both session and API-key principals.
- Postgres Row-Level Security (migration `0004`): every organization-scoped table gets a FORCEd `tenant_isolation` policy driven by a per-transaction `app.organization_id` GUC that the API sets from the authenticated principal. The compose runtime connects as a dedicated non-superuser role (`creativelift_app`, created by a Postgres init script) because superusers bypass RLS; Alembic keeps running as the owner via `ALEMBIC_DATABASE_URL`. The migration smoke test proves cross-tenant reads return zero rows.
- Login UI: `/login` page with account creation, session-aware app shell (organization + user + role chip, Logout), and an automatic redirect to `/login` when the API requires authentication; dev demo mode keeps working without login.
- Redis-backed rate limiting (`RATE_LIMIT_BACKEND=redis`, enabled in compose) with graceful in-memory fallback when Redis is unreachable.
- Event-quality snapshots on ingest are now computed with SQL aggregates on the persistent backend instead of loading every event into memory.
- Daily database backups: a compose sidecar dumps the database (14-day retention) into `./backups`; restore instructions in docs/self-hosting.md.
- Upgrade note: the RLS profile needs the new Postgres init script — reset dev volumes with `docker compose down -v` before `docker compose up --build`.

## Unreleased — every feature real (multi-agent swarm)

- Unified the statistics source: the API measurement service now imports VariantStats, compare_conversion, srm_check and cuped_adjust from services/experiment-engine instead of duplicating them.
- Real sequential testing: `sequential_peek` now implements always-valid mSPRT (normal mixture, log-space; Johari, Koomen, Pekelis & Walsh, KDD 2017). Additive `sequential` block in `POST /v1/demo/analyze` and in experiment results.
- `POST /v1/measurement/mmm-runs` and `POST /v1/measurement/uplift-runs` now compute synchronously via mmm-service and uplift-service, returning `succeeded` with populated outputs (or `failed` with a clear error) instead of empty `queued` records.
- `POST /v1/bandits/{id}/decide` delegates Thompson sampling to bandit-service (`ThompsonBandit.from_state`); the inline copy in the router is gone.
- Connectors are usable end-to-end: real `validate_config()` on all 7 adapters, PostHog `pull()` with cursor pagination over httpx (tests use mocked transports), and a new `POST /v1/connectors/{connector_id}/sync` endpoint (push mode for any provider, pull mode for PostHog) with idempotent replay, event-quality snapshot capture, and connector `last_sync_at`/status updates.
- The api Docker image build context moved to the repository root so the image installs the four statistical services and ships the connectors directory.
- Frontend honesty pass: silent demo fallbacks replaced by a visible "Demo data" badge and a human-readable API error banner with Retry across all 13 data-driven panels; skeleton loaders on dashboard summary and experiment detail.
- Removed dead code: the unmounted `apps/api/app/api/v1/endpoints/events.py` and its orphaned `app/services/events.py`.

## Unreleased — security hardening & real E2E

- Real API-key authentication: keys are HMAC-hashed, resolved against the repository on every request (`Authorization: Bearer` and `X-API-Key`), revocation is immediate, and per-key scopes (e.g. `events:write`) are enforced on ingestion.
- Production safety: demo credentials and anonymous access are rejected outside development, and the API refuses to boot in production with the development pepper or DEBUG enabled.
- Security headers on every response (nosniff, frame deny, referrer policy, permissions policy) and a CSP on the `/demo` console; CORS now allowlists the `X-API-Key` header (fixes browser "Failed to fetch" against the persistent backend).
- Non-root users in both Docker images; CI security job now runs `pip-audit`, `bandit`, and `npm audit` instead of a placeholder.
- Real OpenAI-compatible variant generation: the generator provider now calls chat/completions, parses structured variants, and records model + token usage in prompt lineage (mock provider remains the default).
- First verified Next.js production build; fixed Next 15 async `params` in the three dynamic routes and a demo-fallback type mismatch that broke the build.
- Playwright E2E suite (7 journeys) running against the production web build and a live Postgres-backed API; `make e2e`. README screenshots are captured by the suite from the running product.

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
