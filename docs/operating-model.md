# Operating Model

This document describes how a team would use CreativeLift AI in practice.

## Main Personas

### Growth Marketer

Creates briefs, reviews variants, launches experiments, and reads recommendations.

### Creative Strategist

Defines angle, hook, CTA, offer, brand guardrails, and approved claims.

### Data Analyst

Validates event quality, SRM, lift, confidence, and revenue impact.

### Marketing Engineer

Installs event tracking, connects data sources, and maintains self-hosted infrastructure.

### Agency Operator

Runs the same workflow across multiple client organizations.

## Primary Workflow

```text
1. Create brand pack
2. Create approved claims
3. Create brief
4. Generate or import variants
5. Save each variant as a Creative Treatment
6. Review and approve treatment
7. Create experiment
8. Assign variants and allocation
9. Ingest impression/click/conversion/revenue events
10. Review SRM and lift
11. Make decision
12. Feed learnings into next brief
```

## Screen Ownership

| Screen | Purpose |
| --- | --- |
| `/app/dashboard` | Executive view of lift, confidence, approvals, and ingestion health |
| `/app/briefs` | Planning layer for objectives, audiences, KPIs, and guardrails |
| `/app/creatives` | Creative Treatment registry |
| `/app/creatives/[id]` | Prompt lineage and treatment metadata |
| `/app/experiments` | Experiment registry |
| `/app/experiments/[id]/results` | Statistical result and decision |
| `/app/approvals` | Governance queue |
| `/app/events` | Event ingestion status and examples |
| `/app/connectors` | External data source setup |
| `/app/api-keys` | Scoped ingestion keys |
| `/app/settings` | Organization and data retention settings |

## API Ownership

| API Area | Purpose |
| --- | --- |
| Organizations | Tenant setup |
| Brand packs | Voice, guardrails, regulated category flags |
| Briefs | Marketing objective and testing plan |
| Creative treatments | Measurement unit |
| Variant generation | AI provider abstraction |
| Experiments | Variant allocation and decision rules |
| Events | Ingestion of exposure, conversion, and revenue |
| Results | Lift, SRM, confidence, and recommendation |
| Bandits | Adaptive allocation scaffold |
| Uplift | Batch uplift scoring scaffold |
| MMM | Marketing mix modeling run scaffold |
| API keys | Scoped ingestion credentials |
| Audit logs | Governance history |

## Data Quality Rules

Event ingestion should enforce:

- stable anonymous or user identity
- valid creative treatment ID
- optional experiment and variant IDs
- idempotency keys for retries
- timestamp validation
- currency validation for revenue
- tenant resolution from API key

Experiment analysis should enforce:

- enough sample size
- assignment ratio sanity
- primary metric clarity
- guardrail review
- no decision when SRM fails

## What Happens After A Winner

A winner should not just be celebrated in a dashboard. It should create new structured knowledge:

- winning angle
- winning hook
- winning CTA
- audience segment
- channel and placement
- prompt/model/provider
- claims used
- compliance notes
- revenue impact

That knowledge feeds the next brief and eventually attribution/MMM calibration.

## Current MVP Boundary

Implemented enough to demonstrate and extend:

- route structure
- schema
- local demo data
- validation
- statistical routines
- deterministic assignment and in-memory event-derived results
- dashboard pages
- connector contracts

Not production-complete yet:

- real auth provider
- persistent repository layer for every route
- live vendor connector sync
- assignment policy hardening
- ClickHouse event storage
- production worker queue
- production frontend build verification in this environment
