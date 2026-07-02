# Measurement Methodology

CreativeLift AI starts with credible A/B testing primitives:

- conversion rate per variant
- difference in proportions
- standard error
- z-test p-value
- confidence interval
- absolute and relative lift
- revenue per visitor delta
- sample ratio mismatch check
- CUPED adjustment interface

## Decision Recommendations

- `winner`: statistically significant positive lift and SRM passes.
- `loser`: statistically significant negative lift and SRM passes.
- `inconclusive`: data does not clear the configured threshold.
- `invalid_srm`: assignment ratios are inconsistent with expected allocation.
- `needs_more_data`: sample size is too low.

## Decision Insights

`GET /v1/experiments/{experiment_id}/insights` turns the current experiment result into a decision summary, recommended action, evidence list, and next steps. It is deterministic and derived from the same result object used by the results endpoint.

## Experiment Result Aggregation

The current API computes experiment results from matching in-memory events when an event has the requested `experiment_id` and a known `variant_id`.

- Every event with a known variant counts the user or anonymous ID as a visitor for that variant.
- `signup`, `lead`, `purchase`, `revenue`, and `custom_conversion` count as conversion events.
- Conversions are counted as unique converting visitors per variant.
- Event `value` is summed as revenue for conversion events.
- If no matching events exist, the endpoint returns deterministic demo output for local product exploration.

## CUPED

`cuped_adjust(outcome, pre_experiment_covariate)` requires user-level pre-period covariates. The MVP includes the adjustment function and tests; production usage should store assignment-time covariates and validate variance reduction.

## Sequential Testing

The v0.1.0 sequential interface is a placeholder. Add alpha-spending, always-valid p-values, or Bayesian monitoring before encouraging repeated peeking.
