# CreativeLift AI

**From prompt to profit: measure which AI creatives actually lift revenue.**

CreativeLift AI is the open-source AI marketing measurement platform that tracks every creative from brief and prompt through approval, experiment assignment, event ingestion, causal lift, and revenue impact.

## Why This Exists

AI made content infinite. Measurement became the bottleneck. Creative teams can generate endless ads, emails, landing pages, hooks, and offers, but most stacks still cannot answer which generated asset created incremental business impact.

CreativeLift AI is not another AI copywriter. It is a self-hostable measurement operating system for AI-generated marketing.

## Quickstart

Lightweight verification without installing frontend dependencies or starting Docker:

```bash
python3 -m pytest
npm --workspace apps/web run test
python3 -m compileall -q apps/api services connectors packages/sdk-python
```

Optional full local runtime:

```bash
cp .env.example .env
docker compose up --build
```

Open:

- Web app: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/healthz

## Core Concept: Creative Treatment

A Creative Treatment is the versioned unit of measurement. It connects:

brief -> prompt -> generated creative -> approval -> experiment -> exposure -> conversion -> revenue -> decision

Treatments store audience, objective, channel, angle, hook, CTA, offer, copy, media metadata, model/provider, prompt lineage, brand guardrails, approved claims, human edits, compliance status, spend, revenue, lift estimates, and recommendation.

## How It Works

CreativeLift AI follows one loop:

```text
brand pack -> brief -> prompt run -> generated variant -> creative treatment -> approval -> experiment -> events -> lift result -> decision
```

In practice:

1. Create a brand pack with voice, guardrails, and claims.
2. Create a brief with objective, audience, channel, and KPI.
3. Generate or import creative variants.
4. Save each variant as a Creative Treatment.
5. Approve or reject treatments before launch.
6. Create an experiment with allocation and decision rules.
7. Ingest impressions, clicks, conversions, and revenue.
8. Compute lift, SRM, confidence, and recommendation.
9. Promote, retire, or iterate the creative.

Read [docs/how-it-works.md](docs/how-it-works.md) for the product flow and [docs/software-structure.md](docs/software-structure.md) for the engineering map.
Read [docs/implementation-status.md](docs/implementation-status.md) for the honest current state.

## Architecture

```text
apps/web                  Next.js marketing site and dashboard
apps/api                  FastAPI REST API, auth-ready services, DB models
services/experiment-engine Statistical engine: lift, SRM, CUPED
services/bandit-service   Thompson Sampling scaffold
services/uplift-service   Uplift modeling scaffold
services/mmm-service      MMM run scaffold
connectors/*              Warehouse, analytics, CRM, ad platform adapters
packages/schemas          Shared contracts
infra/*                   Docker, Terraform, Kubernetes scaffolds
docs/*                    Product, security, methodology, self-hosting docs
```

## Documentation Map

- [How It Works](docs/how-it-works.md)
- [MVP Workflows](docs/mvp-workflows.md)
- [Screen To API Map](docs/screen-api-map.md)
- [Implementation Status](docs/implementation-status.md)
- [Data Model Map](docs/data-model-map.md)
- [Persistence Plan](docs/persistence-plan.md)
- [Software Structure](docs/software-structure.md)
- [Operating Model](docs/operating-model.md)
- [Architecture](docs/architecture.md)
- [Creative Treatment Model](docs/creative-treatment-model.md)
- [Measurement Methodology](docs/measurement-methodology.md)
- [Event Ingestion](docs/event-ingestion.md)
- [API Reference](docs/api-reference.md)

Tracking examples live in [examples/sdk-tracking](examples/sdk-tracking).

## Event Ingestion Example

```bash
curl -X POST http://localhost:8000/v1/events/ingest \
  -H "X-API-Key: dev-api-key" \
  -H "Idempotency-Key: evt_demo_001" \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "event_name": "purchase",
      "timestamp": "2026-06-28T10:00:00Z",
      "anonymous_id": "anon_123",
      "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
      "experiment_id": "00000000-0000-0000-0000-000000000201",
      "variant_id": "variant_a",
      "channel": "paid_social",
      "placement": "meta_feed",
      "value": 149.00,
      "currency": "USD",
      "properties": {"order_id": "ord_123"}
    }]
  }'
```

## Local Development

Backend:

```bash
cd apps/api
make dev
make test
make lint
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
npm run build
npm run lint
```

Root:

```bash
make setup
make dev
make test
make lint
```

## What Is Implemented in v0.1.0

- FastAPI app with versioned `/v1` routes, health/readiness, request IDs, API errors, auth/RBAC scaffolds.
- SQLAlchemy models and Alembic migration for the core multi-tenant schema.
- Event ingestion API contract with validation, idempotency shape, API key resolution, rate-limit hooks, event health, and in-memory result aggregation.
- Creative registry, experiment registry with launch validation, approvals, claim evidence, API keys, audit logs, generator endpoints.
- API-backed app screens for onboarding, settings, briefs, generation, Creative Treatments, approvals, experiments, results and insights, events, connectors, dashboard summary/approval/ingestion/lineage, and API keys.
- Repository boundary for modular resources, with an in-memory implementation and tests.
- Measurement engine for event-derived conversion lift, z-test, confidence intervals, SRM, CUPED, and recommendations.
- Thompson Sampling bandit service scaffold.
- Uplift and MMM service scaffolds with explicit future adapters.
- Next.js marketing site and app dashboard routes with API clients and declared demo fallbacks.
- Connector framework scaffolds for PostHog, Rudder, Snowplow, Google Ads, Meta Ads, HubSpot, and generic webhooks.
- Docker Compose, CI, docs, issue templates, and open-source community files.

## Honest Scaffold Areas

Live ad platform sync, warehouse exports, production auth providers, RLS enforcement policies, ClickHouse ingestion, PyMC-Marketing, Meridian, Robyn, EconML, and CausalML integrations are scaffolded for extension and documented as future work.

## Roadmap

1. Replace in-memory demo stores with Postgres repositories route by route.
2. Production auth provider and SSO.
3. Postgres RLS policy migration.
4. ClickHouse-backed event store.
5. Warehouse-native exports.
6. Live PostHog/Rudder/Snowplow sync.
7. Google Ads and Meta Ads metadata sync.
8. Sequential testing implementation.
9. Contextual bandits.
10. MMM calibration with experiment priors.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [docs/contributing.md](docs/contributing.md).

## Security

Never commit secrets. API keys are hashed, only prefixes are stored for display, and tenant isolation is a first-class design constraint. See [SECURITY.md](SECURITY.md).

## License

Apache-2.0
