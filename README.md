# CreativeLift AI

**From prompt to profit: measure which AI creatives actually lift revenue.**

[![CI](https://github.com/Hiberius/creativelift-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/Hiberius/creativelift-ai/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](apps/api/pyproject.toml)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black?logo=next.js)](apps/web/package.json)
[![Tests](https://img.shields.io/badge/tests-103_unit_·_7_E2E-brightgreen)](#verified-not-just-promised)

AI made content infinite. Measurement became the bottleneck. Your team can generate 50 ad variants in an hour — but platform ROAS can't tell you which one creates **incremental revenue**. CreativeLift AI is a self-hostable measurement OS that tracks every AI-generated creative from **brief → prompt → approval → experiment → events → causal lift → decision**.

![CreativeLift AI dashboard](docs/screenshots/02-dashboard.png)

## What it does

- **Creative Treatments** — every variant becomes a versioned, measurable unit: prompt lineage, hook, CTA, offer, compliance status, spend, revenue, lift.
- **Governance before spend** — approval queue with brand guardrails; experiments refuse to launch if approved claims lack evidence.
- **Real experiments, real statistics** — deterministic assignment, lift with confidence intervals, p-values, SRM (broken-randomization) checks, CUPED variance reduction, and a plain-language recommendation: promote, retire, or keep collecting.
- **Event ingestion that survives restarts** — idempotent API/SDK ingestion into Postgres, with event-quality snapshots you can trend over time.
- **AI generation with lineage** — plug any OpenAI-compatible endpoint; every generated variant records model, prompt, and token usage. A deterministic mock provider keeps the quickstart free.

![Experiment results with lift, p-value, SRM and a decision](docs/screenshots/05-experiment-results.png)

## Quickstart

The persistent profile (Postgres, migrations on boot):

```bash
cp .env.example .env
docker compose up --build
```

Open http://localhost:3000 (dashboard) and http://localhost:8000/docs (API). Click **Run demo** on the dashboard to seed a fully measured experiment — 224 events, computed lift, a decision — then restart the stack and watch the data survive.

No Docker? The zero-dependency lab runs entirely in memory:

```bash
python3 -m pytest          # 103 tests, no database needed
cd apps/api && python3 -m uvicorn app.main:app   # then open http://localhost:8000/demo
```

## The loop

```text
brand pack → brief → AI variants → creative treatment → approval (claims need evidence)
   → experiment → event ingestion → lift + SRM + confidence → promote / retire
```

| | |
|---|---|
| ![Approvals queue](docs/screenshots/03-approvals.png) | ![Event quality](docs/screenshots/06-events-health.png) |
| Governance: review every treatment before it spends | Ingestion health with persisted quality trend |

Track events from your site or server in a few lines:

```bash
curl -X POST http://localhost:8000/v1/events/ingest \
  -H "Authorization: Bearer <your-api-key>" \
  -H "Idempotency-Key: evt_001" \
  -H "Content-Type: application/json" \
  -d '{"events": [{"event_name": "purchase", "timestamp": "2026-07-02T10:00:00Z",
       "anonymous_id": "anon_123", "creative_treatment_id": "<treatment-id>",
       "experiment_id": "<experiment-id>", "variant_id": "treatment",
       "value": 149.0, "currency": "USD"}]}'
```

Python and TypeScript SDKs live in [packages/](packages/), browser/server tracking examples in [examples/sdk-tracking/](examples/sdk-tracking/).

## Security by default

- API keys are stored **HMAC-SHA256 hashed** (peppered) and resolved against the database — the raw key is shown exactly once.
- **Scoped keys** (`events:write`, `measurement:read`, …) enforced per endpoint; revocation is immediate.
- **Production guards**: the API refuses to boot in production with development credentials, and demo fallbacks are disabled outside development.
- Security headers on every response, CSP on the demo console, strict CORS, request-size limits, per-key rate limiting.
- **Non-root containers**, and CI runs `pip-audit`, `bandit`, and `npm audit` on every push.

## Verified, not just promised

| Check | What actually runs |
|---|---|
| `python3 -m pytest` | 103 tests: API workflows, both storage backends, auth, idempotency, statistics |
| `make test-sqlalchemy` | The SQLAlchemy backend exercised on SQLite: parity, tenancy, hashing |
| `make migration-smoke` | Alembic upgrade → downgrade → re-upgrade against a disposable Postgres |
| `make e2e` | 7 Playwright journeys against the production build and a live Postgres-backed API |
| `docker compose restart api` | Ingested events, snapshots, and audit logs survive — persistence is real |

Every screenshot in this README was captured by the E2E suite from the running product.

## Architecture

```text
apps/web                   Next.js 15 dashboard (dark, fast, no template feel)
apps/api                   FastAPI · repository boundary with two backends:
                           in-memory (zero-dep quickstart) and SQLAlchemy/Postgres
services/experiment-engine Lift, SRM, CUPED statistics
services/bandit-service    Thompson Sampling
services/uplift-service    Segment-level uplift baseline
services/mmm-service       Media-mix modeling scaffold
connectors/*               7 adapters (Google Ads, Meta, PostHog, HubSpot, Snowplow, Rudder, webhook)
packages/*                 Shared schemas + Python/TS SDKs
```

Deep dives: [How it works](docs/how-it-works.md) · [Measurement methodology](docs/measurement-methodology.md) · [Self-hosting](docs/self-hosting.md) · [Honest implementation status](docs/implementation-status.md) · [API reference](docs/api-reference.md)

## Roadmap

- **v0.2** — live connector sync (PostHog, GA, ad platforms), ClickHouse event store, connector UI
- **v0.3** — contextual bandits, MMM calibration, warehouse-native exports

The [implementation status](docs/implementation-status.md) page says plainly what is working, what is demo, and what is scaffold — we'd rather under-promise.

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Good first areas: a live connector, sequential testing, dashboard polish.

## Credits

Built end-to-end with **Claude Fable 5** and the latest **OpenAI Codex** — including the statistics engine, the security hardening, this README, and the E2E suite that screenshotted itself.

Licensed under [Apache 2.0](LICENSE).
