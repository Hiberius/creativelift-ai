# MVP Workflows

This document defines the first usable CreativeLift AI workflow. It is the product spine for v0.1.x development.

## Workflow 1: Set Up A Measurement Workspace

Goal: a team creates the basic tenant, brand rules, and ingestion credentials.

Primary user: marketing engineer or growth lead.

Screens:

- `/app/onboarding`
- `/app/settings`
- `/app/api-keys`

APIs:

- `POST /v1/organizations`
- `GET /v1/me`
- `POST /v1/brand-packs`
- `GET /v1/brand-packs`
- `POST /v1/api-keys`
- `GET /v1/api-keys`
- `DELETE /v1/api-keys/{api_key_id}`

Data created:

- organization
- brand pack
- API key
- audit log entry

Definition of done:

- user can create or view an organization
- user can create a brand pack
- user can create an API key and see only its prefix after creation
- docs show how to send events with that key

Current MVP status:

- API routes exist
- demo auth principal exists
- `/app/onboarding` can create an organization and a first brand pack
- `/app/settings` loads the current organization/principal and brand packs
- API key generation/hashing scaffold exists
- `/app/api-keys` is wired to list, create, and delete API keys
- persistent repository layer is not wired yet

## Workflow 2: Create A Brief

Goal: a marketer defines what should be tested.

Primary user: growth marketer or creative strategist.

Screens:

- `/app/briefs`
- `/app/briefs/new`

APIs:

- `POST /v1/briefs`
- `GET /v1/briefs`
- `GET /v1/briefs/{brief_id}`

Data created:

- brief
- optional brand pack reference

Required fields:

- objective
- target audience
- channel
- primary KPI
- body or notes

Definition of done:

- user can create a brief
- brief appears in list
- brief can be used by generator and creative treatment creation

Current MVP status:

- API routes exist
- `/app/briefs` loads briefs from the API with a demo fallback
- `/app/briefs/new` posts new briefs to the API
- brand pack selection and post-create redirect are not implemented yet

## Workflow 3: Generate Or Import Creative Variants

Goal: a brief becomes measurable creative variants.

Primary user: marketer or creative strategist.

Screens:

- `/app/briefs/new`
- future: `/app/briefs/{id}`
- `/app/creatives`

APIs:

- `POST /v1/variants/generate`
- `POST /v1/prompt-runs`
- `GET /v1/prompt-runs`
- `POST /v1/creative-treatments`
- `GET /v1/creative-treatments`

Data created:

- prompt run
- generated variant metadata
- creative treatment
- creative version

Provider behavior:

- local demo uses mock provider
- OpenAI-compatible provider is scaffolded and disabled unless configured

Definition of done:

- user can generate variants from a brief without a real API key
- each variant can be saved as a Creative Treatment
- prompt lineage stores provider, model, prompt, temperature, timestamp, and brand pack

Current MVP status:

- mock generator exists
- OpenAI-compatible interface exists
- prompt run routes exist
- `/app/briefs/new` calls the mock generator
- generated variants are previewed in the UI
- generated variants can be saved as Creative Treatments
- `/app/creatives` loads Creative Treatments from the API with a demo fallback

## Workflow 4: Review And Approve Creative Treatments

Goal: no creative launches without governance.

Primary user: reviewer, brand lead, compliance owner.

Screens:

- `/app/approvals`
- `/app/creatives/[id]`
- `/app/settings`

APIs:

- `GET /v1/creative-treatments?status_filter=pending_review`
- `POST /v1/creative-treatments/{creative_id}/approve`
- `POST /v1/creative-treatments/{creative_id}/reject`
- `GET /v1/claim-evidence`
- `POST /v1/claim-evidence`
- `GET /v1/audit-logs`

Data updated:

- creative treatment approval status
- compliance status
- approval review
- claim evidence
- audit log

Definition of done:

- reviewer can approve or reject treatment
- rejected treatment cannot be assigned to a running experiment
- approval decision is auditable

Current MVP status:

- approve/reject API routes exist
- `/app/approvals` loads Creative Treatments, attaches evidence URLs, and calls approve/reject APIs
- `/app/creatives/[id]` loads a Creative Treatment from the API with a demo fallback
- `/app/settings` can list and create claim evidence records
- experiment start blocks variants whose Creative Treatments are missing or not approved
- experiment start blocks approved Creative Treatments that still need claim evidence

## Workflow 5: Create And Run An Experiment

Goal: approved treatments are assigned to variants and measured.

Primary user: growth marketer or analyst.

Screens:

- `/app/experiments`
- `/app/experiments/[id]`
- `/app/experiments/[id]/results`

APIs:

- `POST /v1/experiments`
- `GET /v1/experiments`
- `GET /v1/experiments/{experiment_id}`
- `POST /v1/experiments/{experiment_id}/start`
- `POST /v1/experiments/{experiment_id}/pause`
- `POST /v1/experiments/{experiment_id}/complete`
- `GET /v1/experiments/{experiment_id}/results`

Data created:

- experiment
- experiment variants
- traffic allocation
- decision rule

Definition of done:

- experiment has at least one control and one treatment
- allocations sum to 1.0
- status transitions are explicit
- results endpoint returns recommendation

Current MVP status:

- experiment APIs exist
- allocation validation exists in active schema
- start validation requires at least one control, one treatment, and approved Creative Treatments
- status routes exist
- `/app/experiments` can list, create, start, pause, and complete experiments
- `/app/experiments/[id]` can load experiment detail and trigger status actions
- results aggregate matching in-memory events and fall back to deterministic demo values when no events exist

## Workflow 6: Ingest Events

Goal: CreativeLift AI receives exposure, conversion, and revenue events.

Primary user: marketing engineer or data engineer.

Screens:

- `/app/events`
- `/app/connectors`
- `/app/api-keys`

APIs:

- `POST /v1/events/ingest`
- `GET /v1/events`
- `GET /v1/events/health`
- `GET /v1/connectors`
- `POST /v1/connectors`

Supported event names:

- impression
- click
- session_start
- signup
- lead
- purchase
- revenue
- custom_conversion

Definition of done:

- event requires anonymous ID or user ID
- event requires creative treatment ID
- idempotency key deduplicates retries
- tenant is resolved from API key
- malformed payload receives a clear validation error

Current MVP status:

- ingestion route exists
- validation tests pass
- `/app/events` can send a demo event to `/v1/events/ingest`
- `/app/events` can show event health from `GET /v1/events/health`
- idempotency shape exists
- in-memory event store only
- `/app/connectors` can list and create connector registry records against the API
- live connector sync is scaffolded

## Workflow 7: Read Measurement Results

Goal: user knows whether a creative actually lifted business outcomes.

Primary user: analyst, growth lead, agency operator.

Screens:

- `/app/dashboard`
- `/app/experiments/[id]/results`

APIs:

- `GET /v1/measurement/summary`
- `GET /v1/experiments/{experiment_id}/results`
- `GET /v1/experiments/{experiment_id}/insights`
- `POST /v1/measurement/uplift-runs`
- `POST /v1/measurement/mmm-runs`
- `POST /v1/bandits`
- `POST /v1/bandits/{bandit_id}/decide`
- `POST /v1/bandits/{bandit_id}/update`

Metrics:

- visitors
- conversions
- conversion rate
- absolute lift
- relative lift
- p-value
- confidence interval
- revenue per visitor delta
- SRM p-value
- recommendation

Definition of done:

- result says winner, loser, inconclusive, invalid SRM, or needs more data
- SRM failure blocks winner recommendation
- dashboard shows event health and approval risk alongside lift

Current MVP status:

- statistical routines exist and pass tests
- result endpoint aggregates matching in-memory events and falls back to demo data
- `/app/experiments/[id]/results` loads API results with fallback
- `/app/experiments/[id]/results` loads decision insights with fallback
- `/app/dashboard` loads summary cards from `GET /v1/measurement/summary` with fallback
- `/app/dashboard` loads ingestion quality from `GET /v1/events/health` with fallback
- `/app/dashboard` loads approval risk from Creative Treatments and lineage from audit logs
- persistent DB query aggregation is not implemented yet

## Workflow 8: Feed Learnings Back Into Creative Strategy

Goal: every experiment creates reusable creative intelligence.

Primary user: creative strategist and growth lead.

Screens:

- `/app/creatives/[id]`
- `/app/dashboard`
- future: `/app/insights`

Data captured:

- winning prompt
- winning angle
- winning hook
- winning CTA
- audience segment
- approved claims
- channel and placement
- model/provider
- lift and revenue impact

Definition of done:

- result page links back to prompt and creative treatment
- winning attributes are structured, not buried in notes
- next brief can reuse learnings

Current MVP status:

- lineage UI exists and loads Creative Treatment metadata from the API with fallback
- experiment insight endpoint produces decision summary, evidence, and next steps
- persisted creative insight records are not implemented yet
