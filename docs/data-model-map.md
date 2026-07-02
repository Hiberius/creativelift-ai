# Data Model Map

This map explains why each major table exists.

## Tenant And Access

| Table | Purpose |
| --- | --- |
| `organizations` | Tenant boundary |
| `users` | Human users |
| `memberships` | User role in organization |
| `api_keys` | Scoped service credentials |
| `audit_logs` | Governance and admin history |

## Brand And Planning

| Table | Purpose |
| --- | --- |
| `brand_packs` | Brand voice, guardrails, regulated category flag |
| `approved_claims` | Claims with evidence URLs |
| `claim_evidence` | Evidence library for claims used in creative review |
| `briefs` | Objective, audience, channel, KPI, and test plan |

## Creative Lineage

| Table | Purpose |
| --- | --- |
| `prompt_runs` | Provider, model, prompt, system prompt, temperature, output |
| `creative_treatments` | Central measurable creative object |
| `creative_versions` | Version history and human edits |
| `approval_reviews` | Reviewer decision, evidence, and notes |

## Experimentation

| Table | Purpose |
| --- | --- |
| `experiments` | Hypothesis, metric, status, channel, decision rule |
| `experiment_variants` | Variant allocation and control/treatment mapping |
| `events` | Impression, click, conversion, purchase, and revenue events |
| `experiment_results` | Computed results and recommendation |

## Advanced Measurement

| Table | Purpose |
| --- | --- |
| `bandits` | Adaptive allocation policy |
| `bandit_arms` | Arm priors and creative mapping |
| `uplift_runs` | Batch uplift scoring jobs |
| `mmm_runs` | Marketing mix modeling jobs |

## Integrations

| Table | Purpose |
| --- | --- |
| `connectors` | External system configuration and sync status |

## Relationship Spine

```text
organization
  -> brand_pack
  -> brief
  -> prompt_run
  -> creative_treatment
  -> creative_version
  -> approval_review
  -> experiment_variant
  -> experiment
  -> event
  -> experiment_result
```

Not every row has every relationship in v0.1.0, but this is the intended spine.
