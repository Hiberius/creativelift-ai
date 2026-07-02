# Software Structure

This repository is a monorepo. Each area owns a different part of the product.

## Top-Level Map

```text
apps/web                  Product UI and marketing site
apps/api                  FastAPI backend
services/experiment-engine Statistical measurement package
services/bandit-service   Thompson Sampling package
services/uplift-service   Uplift modeling package
services/mmm-service      MMM package
connectors                External system adapters
packages/schemas          Shared TypeScript contracts
packages/sdk-ts           TypeScript SDK
packages/sdk-python       Python SDK
dbt                       Warehouse model scaffold
infra                     Deployment scaffolds
docs                      Product and engineering docs
examples                  Demo use cases and seed data
```

## Frontend

Path: `apps/web`

Responsibilities:

- marketing pages
- SEO metadata
- product dashboard
- demo tables and charts
- app shell and navigation
- route structure for the future SaaS product

Important routes:

- `/`
- `/product`
- `/pricing`
- `/docs`
- `/app/dashboard`
- `/app/briefs`
- `/app/creatives`
- `/app/experiments`
- `/app/events`
- `/app/connectors`
- `/app/api-keys`

## Backend

Path: `apps/api`

Responsibilities:

- REST API under `/v1`
- OpenAPI docs
- request IDs
- CORS
- request size limits
- rate limiting hooks
- auth/API key scaffolds
- RBAC scaffolds
- validation
- event ingestion
- AI generation provider abstraction
- experiment result APIs

Important files:

- `app/main.py`: app factory and system routes
- `app/api/v1/router.py`: public v1 route surface
- `app/schemas/common.py`: active API schemas
- `app/db/models.py`: active SQLAlchemy database schema
- `app/db/session.py`: SQLAlchemy engine/session runtime
- `app/services/repositories.py`: repository contracts for replacing demo storage
- `app/services/core_repositories.py`: core repository boundary for organization bootstrap, API keys, audit logs, brand packs, briefs, Creative Treatments, experiments, bandit state, demo measurement runs, claim evidence, and events
- `app/services/demo_store.py`: local in-memory demo data
- `app/services/generator.py`: mock and OpenAI-compatible generation interface
- `app/services/measurement.py`: API-facing measurement routines

## Database

Path: `apps/api/app/db`

The database model is multi-tenant and Postgres-first.

Core tables:

- organizations
- users
- memberships
- api_keys
- brand_packs
- approved_claims
- briefs
- creative_treatments
- creative_versions
- prompt_runs
- approval_reviews
- experiments
- experiment_variants
- events
- experiment_results
- bandits
- bandit_arms
- mmm_runs
- uplift_runs
- connectors
- audit_logs

Every tenant-owned table includes `organization_id`.

## Measurement Services

Path: `services`

These packages are intentionally separate from the API so they can later run in workers or batch jobs.

### Experiment Engine

Path: `services/experiment-engine`

Owns:

- conversion rate comparison
- difference in proportions
- z-test
- p-value
- confidence interval
- relative lift
- revenue per visitor delta
- SRM check
- CUPED adjustment
- sequential testing interface placeholder

### Bandit Service

Path: `services/bandit-service`

Owns:

- Bernoulli Thompson Sampling
- arm update logic
- future contextual bandit adapter

### Uplift Service

Path: `services/uplift-service`

Owns:

- two-model baseline interface
- segment uplift scoring
- future EconML/CausalML adapters

### MMM Service

Path: `services/mmm-service`

Owns:

- demo weekly contribution model
- future PyMC-Marketing, Meridian, and Robyn adapters
- calibration notes from experiment lift

## Connectors

Path: `connectors`

Connectors normalize external systems into CreativeLift AI records.

Current scaffolds:

- PostHog
- Rudder
- Snowplow
- Google Ads
- Meta Ads
- HubSpot
- generic webhook

Each connector has:

- README
- config schema
- adapter shape
- contract test

## Shared Packages

### `packages/schemas`

Shared TypeScript contracts for events, treatments, experiments, and results.

### `packages/sdk-ts`

Small TypeScript ingestion client.

### `packages/sdk-python`

Small Python ingestion client.

## Local Runtime

`docker-compose.yml` defines:

- Postgres
- Redis
- API
- Web

This was not executed during the lightweight stabilization pass.
