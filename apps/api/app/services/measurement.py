from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from experiment_engine import (
    VariantStats,
    compare_conversion,
    cuped_adjust,
    sequential_peek,
    srm_check,
)

from app.schemas.common import MeasurementAnalysisRead, MeasurementAnalyzeRequest
from app.schemas.domain import MeasurementSummary, MetricCard

# Statistical primitives come from the standalone experiment-engine service;
# VariantStats, cuped_adjust and srm_check are re-exported here for callers.
__all__ = [
    "VariantStats",
    "compare_proportions",
    "cuped_adjust",
    "sequential_peek",
    "srm_check",
    "analyze_observed_variants",
    "demo_experiment_result",
    "experiment_result_from_events",
    "MeasurementService",
    "measurement_service",
]

CONVERSION_EVENT_NAMES = {"signup", "lead", "purchase", "revenue", "custom_conversion"}


def compare_proportions(control: VariantStats, treatment: VariantStats) -> dict[str, float | str]:
    """Shim over experiment_engine.compare_conversion.

    Keeps the historical API behavior of analyzing any variant with at least
    one visitor, while the engine default requires 30 visitors per arm.
    """
    return compare_conversion(control, treatment, min_visitors=1)


def _pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def _sample_size_plan(baseline_rate: float, mde: float | None, control_visitors: int, treatment_visitors: int) -> dict[str, Any]:
    effect = mde or 0.01
    if baseline_rate <= 0:
        return {
            "minimum_detectable_effect": effect,
            "per_variant": None,
            "remaining_control": None,
            "remaining_treatment": None,
            "note": "Need a non-zero baseline conversion rate to estimate sample size.",
        }
    z_alpha = 1.96
    z_beta = 0.84
    per_variant = int(max(1, round(2 * ((z_alpha + z_beta) ** 2) * baseline_rate * (1 - baseline_rate) / (effect**2))))
    return {
        "minimum_detectable_effect": effect,
        "per_variant": per_variant,
        "remaining_control": max(0, per_variant - control_visitors),
        "remaining_treatment": max(0, per_variant - treatment_visitors),
        "note": "Approximate two-sided 95% confidence, 80% power sample estimate.",
    }


def analyze_observed_variants(payload: MeasurementAnalyzeRequest) -> MeasurementAnalysisRead:
    control = VariantStats(
        key=payload.control.key,
        visitors=payload.control.visitors,
        conversions=payload.control.conversions,
        revenue=payload.control.revenue,
    )
    treatment = VariantStats(
        key=payload.treatment.key,
        visitors=payload.treatment.visitors,
        conversions=payload.treatment.conversions,
        revenue=payload.treatment.revenue,
    )
    comparison = compare_proportions(control, treatment)
    sequential = sequential_peek(control, treatment)
    allocation_total = payload.control.allocation + payload.treatment.allocation
    expected_allocation = {
        control.key: payload.control.allocation / allocation_total,
        treatment.key: payload.treatment.allocation / allocation_total,
    }
    srm = srm_check(
        {control.key: control.visitors, treatment.key: treatment.visitors},
        expected_allocation,
    )
    recommendation = "invalid_srm" if not srm["passed"] else str(comparison.get("decision", "needs_more_data"))
    p_value = comparison.get("p_value")
    confidence = 1 - float(p_value) if isinstance(p_value, float) else 0.0
    sample_size = _sample_size_plan(
        control.conversion_rate,
        payload.minimum_detectable_effect,
        control.visitors,
        treatment.visitors,
    )

    if recommendation == "winner":
        decision_summary = (
            f"{payload.treatment.label or treatment.key} is ahead by "
            f"{_pct(float(comparison['absolute_lift']))} absolute lift "
            f"({_pct(float(comparison['relative_lift']))} relative lift)."
        )
        recommended_action = "Promote the treatment after checking brand and revenue guardrails."
    elif recommendation == "loser":
        decision_summary = (
            f"{payload.treatment.label or treatment.key} underperforms the control by "
            f"{_pct(abs(float(comparison['absolute_lift'])))} absolute conversion rate."
        )
        recommended_action = "Keep the control live and archive or rework the treatment."
    elif recommendation == "invalid_srm":
        decision_summary = "Traffic split looks imbalanced enough to invalidate the read."
        recommended_action = "Fix assignment or tracking before making a creative decision."
    elif recommendation == "needs_more_data":
        decision_summary = "At least one variant has no visitors, so the test cannot be read yet."
        recommended_action = "Send exposure and conversion events before reading the experiment."
    else:
        decision_summary = (
            f"The treatment is at {_pct(treatment.conversion_rate)} vs control at "
            f"{_pct(control.conversion_rate)}, but the result is not decisive yet."
        )
        recommended_action = "Keep the test running until confidence or the planned sample size improves."

    next_steps = [
        f"Confidence estimate: {_pct(max(0.0, min(confidence, 1.0)))}.",
        f"SRM p-value: {float(srm['p_value']):.4f}.",
    ]
    if sample_size["per_variant"] is not None:
        next_steps.append(
            f"Target about {sample_size['per_variant']:,} visitors per variant for "
            f"{_pct(float(sample_size['minimum_detectable_effect']))} minimum detectable lift."
        )
    if recommendation in {"winner", "loser"}:
        next_steps.append("Attach claim evidence and campaign context before recording the final decision.")

    return MeasurementAnalysisRead(
        name=payload.name,
        primary_metric=payload.primary_metric,
        variants={
            control.key: {
                "key": control.key,
                "label": payload.control.label or control.key,
                "visitors": control.visitors,
                "conversions": control.conversions,
                "revenue": control.revenue,
                "allocation": payload.control.allocation,
                "conversion_rate": control.conversion_rate,
                "revenue_per_visitor": control.revenue_per_visitor,
            },
            treatment.key: {
                "key": treatment.key,
                "label": payload.treatment.label or treatment.key,
                "visitors": treatment.visitors,
                "conversions": treatment.conversions,
                "revenue": treatment.revenue,
                "allocation": payload.treatment.allocation,
                "conversion_rate": treatment.conversion_rate,
                "revenue_per_visitor": treatment.revenue_per_visitor,
            },
        },
        comparison=comparison,
        srm=srm,
        sample_size=sample_size,
        sequential=sequential,
        recommendation=recommendation,
        decision_summary=decision_summary,
        recommended_action=recommended_action,
        next_steps=next_steps,
    )


def demo_experiment_result(experiment_id: str) -> dict:
    control = VariantStats(key="control", visitors=12000, conversions=720, revenue=178000)
    treatment = VariantStats(key="ai_video", visitors=12180, conversions=862, revenue=248000)
    comparison = compare_proportions(control, treatment)
    srm = srm_check({"control": control.visitors, "ai_video": treatment.visitors}, {"control": 0.5, "ai_video": 0.5})
    recommendation = "invalid_srm" if not srm["passed"] else comparison["decision"]
    return {
        "experiment_id": experiment_id,
        "variants": {
            control.key: control.__dict__ | {"conversion_rate": control.conversion_rate},
            treatment.key: treatment.__dict__ | {"conversion_rate": treatment.conversion_rate},
        },
        "comparison": comparison,
        "srm": srm,
        "sequential": sequential_peek(control, treatment),
        "recommendation": recommendation,
    }


def _event_name_value(event_name: Any) -> str:
    return str(getattr(event_name, "value", event_name))


def _event_actor(event: Any) -> str:
    return str(event.user_id or event.anonymous_id)


def experiment_result_from_events(experiment_id: str, variants: list[Any], events: list[Any]) -> dict | None:
    if len(variants) < 2:
        return None
    variant_keys = {variant.key for variant in variants}
    aggregates = {
        variant.key: {"visitors": set(), "converters": set(), "revenue": 0.0}
        for variant in variants
    }
    matched_known_variant = False

    for event in events:
        if str(event.experiment_id) != experiment_id or not event.variant_id:
            continue
        variant_key = str(event.variant_id)
        if variant_key not in variant_keys:
            continue
        matched_known_variant = True
        aggregate = aggregates[variant_key]
        actor = _event_actor(event)
        aggregate["visitors"].add(actor)
        if _event_name_value(event.event_name) in CONVERSION_EVENT_NAMES:
            aggregate["converters"].add(actor)
            aggregate["revenue"] += float(event.value or 0.0)

    if not matched_known_variant:
        return None

    variant_stats = {
        key: VariantStats(
            key=key,
            visitors=len(values["visitors"]),
            conversions=len(values["converters"]),
            revenue=float(values["revenue"]),
        )
        for key, values in aggregates.items()
    }
    control_variant = next((variant for variant in variants if variant.is_control), variants[0])
    treatment_variant = next((variant for variant in variants if not variant.is_control), variants[-1])
    comparison = compare_proportions(
        variant_stats[control_variant.key],
        variant_stats[treatment_variant.key],
    )
    total_allocation = sum(float(variant.allocation) for variant in variants)
    expected_allocation = {
        variant.key: float(variant.allocation) / total_allocation
        for variant in variants
        if total_allocation > 0
    }
    observed = {key: stats.visitors for key, stats in variant_stats.items()}
    srm = srm_check(observed, expected_allocation)
    recommendation = "invalid_srm" if not srm["passed"] else comparison["decision"]
    return {
        "experiment_id": experiment_id,
        "variants": {
            key: stats.__dict__
            | {
                "conversion_rate": stats.conversion_rate,
                "revenue_per_visitor": stats.revenue_per_visitor,
            }
            for key, stats in variant_stats.items()
        },
        "comparison": comparison,
        "srm": srm,
        "sequential": sequential_peek(
            variant_stats[control_variant.key],
            variant_stats[treatment_variant.key],
        ),
        "recommendation": recommendation,
    }


_SUMMARY_WINDOW_DAYS = {"last_7_days": 7, "last_30_days": 30, "last_90_days": 90}


class MeasurementService:
    """Aggregates measurement summary cards from the repository.

    Falls back to the deterministic demo cards when the organization has no
    ingested events, so the dashboard keeps working out of the box.
    """

    def __init__(self, repository: Any | None = None) -> None:
        self._repository = repository

    def _resolve_repository(self) -> Any:
        if self._repository is not None:
            return self._repository
        from app.services.core_repositories import core_repository

        return core_repository

    @staticmethod
    def _window_start(window: str) -> datetime | None:
        days = _SUMMARY_WINDOW_DAYS.get(window)
        if days is None:
            return None
        return datetime.now(UTC) - timedelta(days=days)

    @staticmethod
    def _demo_summary(organization_id: UUID, window: str) -> MeasurementSummary:
        return MeasurementSummary(
            organization_id=organization_id,
            window=window,
            cards=[
                MetricCard(metric="impressions", value=128_420, delta=0.12),
                MetricCard(metric="conversion_rate", value=0.043, delta=0.006, unit="ratio"),
                MetricCard(metric="incremental_lift", value=0.087, delta=0.014, unit="ratio"),
                MetricCard(metric="creative_fatigue_index", value=0.31, delta=-0.04, unit="score"),
            ],
            notes=[
                "Demo values are deterministic scaffolds until warehouse queries are wired.",
                "MMM and uplift services expose run resources for later async workers.",
            ],
        )

    @staticmethod
    def _observed_lift(repository: Any, organization_id: UUID) -> tuple[float, str]:
        events = repository.list_events(organization_id, limit=None)
        for experiment in repository.list_experiments(organization_id):
            result = experiment_result_from_events(str(experiment.id), experiment.variants, events)
            if result:
                lift = float(result["comparison"]["relative_lift"])
                return lift, f"Incremental lift read from experiment '{experiment.name}'."
        return 0.0, "No experiment has readable event-derived results yet."

    async def summary(self, organization_id: UUID, window: str = "last_7_days") -> MeasurementSummary:
        repository = self._resolve_repository()
        stats = repository.measurement_summary_stats(organization_id, since=self._window_start(window))
        if stats.total_events == 0:
            return self._demo_summary(organization_id, window)

        conversion_rate = stats.conversion_events / stats.unique_actors if stats.unique_actors else 0.0
        lift_value, lift_note = self._observed_lift(repository, organization_id)
        return MeasurementSummary(
            organization_id=organization_id,
            window=window,
            cards=[
                MetricCard(metric="impressions", value=float(stats.total_events)),
                MetricCard(metric="conversion_rate", value=round(conversion_rate, 4), unit="ratio"),
                MetricCard(metric="incremental_lift", value=round(lift_value, 4), unit="ratio"),
                MetricCard(metric="creative_fatigue_index", value=0.31, unit="score"),
            ],
            notes=[
                f"Computed from {stats.total_events} repository events in window '{window}'.",
                (
                    f"{stats.running_experiments} running experiments, "
                    f"{stats.pending_review_creatives} creatives awaiting review, "
                    f"{stats.approved_creatives} approved."
                ),
                lift_note,
                "creative_fatigue_index is not yet computed from events.",
            ],
        )


measurement_service = MeasurementService()
