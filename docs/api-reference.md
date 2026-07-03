# API Reference

The API is versioned under `/v1`. FastAPI exposes generated OpenAPI docs at `/docs` when the API server is running.

The no-dependency local product demo is available at `/demo` when the API server is running.

## Auth

Local demo routes accept the built-in demo principal when no `Authorization` header is present.

API-key protected modular routes use:

```text
X-API-Key: dev-api-key
```

The frontend reads this from `NEXT_PUBLIC_DEMO_API_KEY` and defaults to `dev-api-key` for local demo mode.

## Workspace

- `POST /v1/demo/analyze`
- `POST /v1/demo/reports`
- `GET /v1/demo/reports`
- `DELETE /v1/demo/reports`
- `GET /v1/demo/reports/export`
- `POST /v1/demo/reports/import`
- `GET /v1/demo/reports/summary`
- `POST /v1/demo/scenario`
- `POST /v1/organizations`
- `GET /v1/me`
- `POST /v1/brand-packs`
- `GET /v1/brand-packs`
- `POST /v1/claim-evidence`
- `GET /v1/claim-evidence`
- `POST /v1/api-keys`
- `GET /v1/api-keys`
- `DELETE /v1/api-keys/{api_key_id}`
- `GET /v1/audit-logs`

## Briefs And Generation

- `POST /v1/briefs`
- `GET /v1/briefs`
- `GET /v1/briefs/{brief_id}`
- `POST /v1/variants/generate`
- `POST /v1/prompt-runs`
- `GET /v1/prompt-runs`

## Creative Treatments

- `POST /v1/creative-treatments`
- `GET /v1/creative-treatments`
- `GET /v1/creative-treatments/{creative_id}`
- `POST /v1/creative-treatments/{creative_id}/approve`
- `POST /v1/creative-treatments/{creative_id}/reject`

## Experiments

- `POST /v1/experiments`
- `GET /v1/experiments`
- `GET /v1/experiments/{experiment_id}`
- `GET /v1/experiments/{experiment_id}/assign`
- `GET /v1/experiments/{experiment_id}/insights`
- `POST /v1/experiments/{experiment_id}/start`
- `POST /v1/experiments/{experiment_id}/pause`
- `POST /v1/experiments/{experiment_id}/complete`
- `GET /v1/experiments/{experiment_id}/results`

## Events

- `GET /v1/events`
- `GET /v1/events/health`
- `GET /v1/events/health/history`
- `POST /v1/events/ingest`

## Measurement

- `GET /v1/measurement/summary`
- `POST /v1/measurement/mmm-runs`
- `GET /v1/measurement/mmm-runs`
- `POST /v1/measurement/uplift-runs`
- `GET /v1/measurement/uplift-runs`
- `POST /v1/uplift/runs`
- `GET /v1/uplift/runs/{run_id}`
- `POST /v1/mmms/runs`
- `GET /v1/mmms/runs/{run_id}`

## Adaptive Allocation

- `POST /v1/bandits`
- `POST /v1/bandits/{bandit_id}/decide`
- `POST /v1/bandits/{bandit_id}/update`

## Connectors

- `POST /v1/connectors`
- `GET /v1/connectors`
- `POST /v1/connectors/{connector_id}/sync`

## Response Shapes

Core demo routes return the resource directly, for example `GET /v1/briefs` returns a JSON array.

Modular repository-backed routes return envelopes:

```json
{
  "data": [],
  "meta": {
    "total": 0,
    "limit": 50,
    "offset": 0
  }
}
```
