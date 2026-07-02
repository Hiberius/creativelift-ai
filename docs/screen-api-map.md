# Screen To API Map

This map connects product screens to backend routes and data ownership. It should be updated whenever a route or page changes.

## App Screens

| Screen | Primary Purpose | Reads | Writes | Status |
| --- | --- | --- | --- | --- |
| `/demo` | No-dependency local measurement lab | `GET /v1/demo/reports`, `GET /v1/demo/reports/summary`, `GET /v1/demo/reports/export` | `POST /v1/demo/analyze`, `POST /v1/demo/reports`, `POST /v1/demo/reports/import`, `DELETE /v1/demo/reports`, `POST /v1/demo/scenario` | FastAPI-served calculator, CSV import, persistent decision log, portfolio summary, export, and scenario runner wired |
| `/app/onboarding` | First-run setup | `GET /v1/me`, `GET /v1/brand-packs` | `POST /v1/organizations`, `POST /v1/brand-packs` | API client wired |
| `/app/dashboard` | Lift, confidence, approvals, ingestion health | `GET /v1/measurement/summary`, `GET /v1/creative-treatments`, `GET /v1/events/health`, `GET /v1/audit-logs` | `POST /v1/demo/scenario` | Summary, demo scenario launcher, approval risk, event health, and lineage API clients wired |
| `/app/briefs` | Brief registry | `GET /v1/briefs` | none | API client wired with demo fallback |
| `/app/briefs/new` | Create brief and generate variants | none | `POST /v1/briefs`, `POST /v1/variants/generate` | API client wired |
| `/app/creatives` | Creative Treatment registry | `GET /v1/creative-treatments` | `POST /v1/creative-treatments` from `/app/briefs/new` | API client wired with demo fallback |
| `/app/creatives/[id]` | Treatment metadata and lineage | `GET /v1/creative-treatments/{creative_id}` | approve/reject actions later | API client wired with demo fallback |
| `/app/experiments` | Experiment registry | `GET /v1/experiments` | `POST /v1/experiments`, validated status actions | API client wired |
| `/app/experiments/[id]` | Experiment detail | `GET /v1/experiments/{experiment_id}`, `GET /v1/experiments/{experiment_id}/assign` | start/pause/complete | API client wired with demo fallback |
| `/app/experiments/[id]/results` | Measurement result | `GET /v1/experiments/{experiment_id}/results`, `GET /v1/experiments/{experiment_id}/insights` | none | API client wired with demo fallback |
| `/app/approvals` | Review queue | `GET /v1/creative-treatments` | approve/reject | API client wired |
| `/app/events` | Ingestion status and examples | `GET /v1/events`, `GET /v1/events/health` | `POST /v1/events/ingest` | API client wired for demo send, recent events, and event health |
| `/app/connectors` | Connector setup | `GET /v1/connectors` | `POST /v1/connectors` | API client wired with demo fallback |
| `/app/settings` | Organization settings | `GET /v1/me`, `GET /v1/brand-packs`, `GET /v1/claim-evidence`, `GET /v1/audit-logs` | `POST /v1/claim-evidence` | API client wired |
| `/app/api-keys` | Ingestion credentials | `GET /v1/api-keys` | `POST /v1/api-keys`, `DELETE /v1/api-keys/{api_key_id}` | API client wired |

## Marketing Screens

| Screen | Purpose |
| --- | --- |
| `/` | Main SEO landing page |
| `/product` | Product overview |
| `/use-cases/ai-creative-testing` | AI creative testing keyword page |
| `/use-cases/marketing-attribution` | Attribution keyword page |
| `/use-cases/agencies` | Agency use case |
| `/use-cases/b2b-saas` | B2B SaaS use case |
| `/use-cases/ecommerce` | E-commerce use case |
| `/open-source` | Open-source positioning |
| `/security` | Security positioning |
| `/docs` | Docs landing |
| `/blog` | Seed blog index |
| `/compare/*` | Respectful competitor comparison pages |
| `/pricing` | Open-source and future cloud pricing |
| `/github` | Repo CTA and description |

## API Route Groups

| Route Group | Owner | Product Concept |
| --- | --- | --- |
| `/v1/organizations` | tenant setup | Organization |
| `/v1/demo/analyze` | measurement | Manual Experiment Analysis |
| `/v1/demo/reports` | measurement | Saved Measurement Decision |
| `/v1/demo/reports/export` | measurement | Measurement Report Export |
| `/v1/demo/reports/import` | measurement | CSV Measurement Import |
| `/v1/demo/reports/summary` | measurement | Measurement Report Portfolio Summary |
| `/v1/demo/scenario` | demo workflow | Workspace, Creative Treatment, Experiment Result |
| `/v1/me` | auth/session | Principal and tenant |
| `/v1/brand-packs` | brand governance | Brand Pack |
| `/v1/claim-evidence` | brand governance | Claim Evidence |
| `/v1/briefs` | planning | Brief |
| `/v1/prompt-runs` | provenance | Prompt Run |
| `/v1/variants/generate` | AI gateway | Generated Variant |
| `/v1/creative-treatments` | registry | Creative Treatment |
| `/v1/creative-treatments/{id}/approve` | governance | Approval Review |
| `/v1/experiments` | experimentation | Experiment |
| `/v1/events` | data collection | Event list |
| `/v1/events/health` | data quality | Event health |
| `/v1/events/ingest` | data collection | Event ingest |
| `/v1/experiments/{id}/results` | measurement | Experiment Result |
| `/v1/experiments/{id}/insights` | measurement | Experiment Insight |
| `/v1/measurement/*` | reporting | Summary, Uplift, MMM |
| `/v1/bandits/*` | adaptive allocation | Bandit |
| `/v1/connectors` | integrations | Connector |
| `/v1/api-keys` | developer/admin | API Key |
| `/v1/audit-logs` | governance | Audit Log |

## Next Frontend Integration Order

1. Persist API routes with Postgres repositories.
2. Add persistent event quality trend storage.
3. Add browser E2E once dependencies are intentionally installed.
4. Add persistent operator-facing audit/event views.
