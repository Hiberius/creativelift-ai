from __future__ import annotations

from typing import Any

from app.schemas.common import ExperimentInsightRead, ExperimentRead


def _pct(value: Any) -> str:
    return f"{value * 100:.2f}%" if isinstance(value, int | float) else "-"


def _num(value: Any, digits: int = 4) -> str:
    return f"{value:.{digits}f}" if isinstance(value, int | float) else "-"


def _primary_variant_keys(experiment: ExperimentRead) -> tuple[str, str]:
    control = next((variant for variant in experiment.variants if variant.is_control), experiment.variants[0])
    treatment = next((variant for variant in experiment.variants if not variant.is_control), experiment.variants[-1])
    return control.key, treatment.key


def build_experiment_insight(experiment: ExperimentRead, result: dict[str, Any]) -> ExperimentInsightRead:
    control_key, treatment_key = _primary_variant_keys(experiment)
    comparison = result.get("comparison", {})
    srm = result.get("srm", {})
    recommendation = str(result.get("recommendation", "inconclusive"))
    winning_variant_key: str | None = None

    if recommendation == "winner":
        winning_variant_key = treatment_key
        decision_summary = f"{treatment_key} is the current winner for {experiment.primary_metric}."
        recommended_action = "Promote the winning treatment and keep monitoring guardrails."
    elif recommendation == "loser":
        winning_variant_key = control_key
        decision_summary = f"{treatment_key} underperforms the control for {experiment.primary_metric}."
        recommended_action = "Retire the treatment and iterate on the brief or creative angle."
    elif recommendation == "invalid_srm":
        decision_summary = "Traffic allocation does not match the expected experiment split."
        recommended_action = "Hold the decision and inspect assignment, targeting, and event tracking."
    elif recommendation == "needs_more_data":
        decision_summary = "The experiment does not have enough data for a decision."
        recommended_action = "Keep running until the minimum sample and guardrail checks are satisfied."
    else:
        decision_summary = "The experiment is not statistically decisive yet."
        recommended_action = "Keep collecting data or launch a sharper treatment hypothesis."

    evidence = [
        f"Control conversion rate: {_pct(comparison.get('control_rate'))}",
        f"Treatment conversion rate: {_pct(comparison.get('treatment_rate'))}",
        f"Absolute lift: {_pct(comparison.get('absolute_lift'))}",
        f"Relative lift: {_pct(comparison.get('relative_lift'))}",
        f"p-value: {_num(comparison.get('p_value'))}",
        f"SRM p-value: {_num(srm.get('p_value'), 3)}",
    ]
    revenue_delta = comparison.get("revenue_per_visitor_delta")
    if isinstance(revenue_delta, int | float):
        evidence.append(f"Revenue per visitor delta: {revenue_delta:.2f}")

    next_steps = [
        "Review event health before acting on the decision.",
        "Check rejected or pending Creative Treatments before scaling.",
    ]
    if recommendation in {"winner", "loser"}:
        next_steps.append("Feed the winning and losing angles into the next brief.")
    if recommendation == "invalid_srm":
        next_steps.append("Verify assignment keys are stable across exposure and conversion events.")
    if recommendation in {"inconclusive", "needs_more_data"}:
        next_steps.append("Revisit minimum detectable effect and sample-size expectations.")

    return ExperimentInsightRead(
        experiment_id=experiment.id,
        recommendation=recommendation,
        winning_variant_key=winning_variant_key,
        decision_summary=decision_summary,
        recommended_action=recommended_action,
        confidence_note=f"Decision rule: {experiment.decision_rule}",
        evidence=evidence,
        next_steps=next_steps,
    )
