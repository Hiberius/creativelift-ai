# Experiment Design

Experiments include:

- name
- hypothesis
- primary metric
- guardrail metric
- variants
- traffic allocation
- randomization unit
- start/end date
- channel
- decision rule
- minimum detectable effect

Statuses:

- draft
- running
- paused
- completed
- invalidated

Assignment:

- `GET /v1/experiments/{experiment_id}/assign?unit_id=...` returns a stable variant for a unit.
- Allocation follows the experiment variant weights.

Launch validation:

- experiment must have at least one control and one treatment
- each variant must reference a Creative Treatment
- referenced Creative Treatments must be approved before start
