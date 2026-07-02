from types import SimpleNamespace

from app.services.measurement import (
    VariantStats,
    analyze_observed_variants,
    compare_proportions,
    cuped_adjust,
    experiment_result_from_events,
    srm_check,
)
from app.schemas.common import MeasurementAnalyzeRequest, MeasurementVariantInput


def test_compare_proportions_detects_winner() -> None:
    control = VariantStats(key="control", visitors=10_000, conversions=500)
    treatment = VariantStats(key="variant", visitors=10_000, conversions=650)
    result = compare_proportions(control, treatment)
    assert result["decision"] == "winner"
    assert result["absolute_lift"] > 0
    assert result["p_value"] < 0.05


def test_analyze_observed_variants_returns_actionable_winner() -> None:
    payload = MeasurementAnalyzeRequest(
        name="Landing page proof test",
        minimum_detectable_effect=0.02,
        control=MeasurementVariantInput(
            key="control",
            label="Current landing page",
            visitors=1000,
            conversions=80,
            revenue=12_000,
        ),
        treatment=MeasurementVariantInput(
            key="proof_page",
            label="Proof-led landing page",
            visitors=1000,
            conversions=130,
            revenue=21_500,
        ),
    )

    analysis = analyze_observed_variants(payload)

    assert analysis.recommendation == "winner"
    assert analysis.variants["proof_page"]["conversion_rate"] == 0.13
    assert analysis.comparison["relative_lift"] > 0
    assert analysis.sample_size["per_variant"] > 0
    assert "Promote" in analysis.recommended_action


def test_srm_check_fails_large_imbalance() -> None:
    result = srm_check({"a": 9000, "b": 1000}, {"a": 0.5, "b": 0.5})
    assert result["passed"] is False


def test_cuped_adjust_preserves_length_and_reduces_linear_covariate_effect() -> None:
    adjusted = cuped_adjust([10, 12, 14, 16], [1, 2, 3, 4])
    assert len(adjusted) == 4
    assert max(adjusted) - min(adjusted) < 1e-9


def test_experiment_result_from_events_aggregates_known_variants() -> None:
    experiment_id = "00000000-0000-0000-0000-000000000999"
    variants = [
        SimpleNamespace(key="control", allocation=0.5, is_control=True),
        SimpleNamespace(key="treatment", allocation=0.5, is_control=False),
    ]
    events = [
        SimpleNamespace(
            experiment_id=experiment_id,
            variant_id="control",
            event_name="impression",
            user_id=None,
            anonymous_id="control-1",
            value=None,
        ),
        SimpleNamespace(
            experiment_id=experiment_id,
            variant_id="control",
            event_name="signup",
            user_id=None,
            anonymous_id="control-1",
            value=0,
        ),
        SimpleNamespace(
            experiment_id=experiment_id,
            variant_id="treatment",
            event_name="impression",
            user_id=None,
            anonymous_id="treatment-1",
            value=None,
        ),
        SimpleNamespace(
            experiment_id=experiment_id,
            variant_id="treatment",
            event_name="purchase",
            user_id=None,
            anonymous_id="treatment-1",
            value=42,
        ),
    ]

    result = experiment_result_from_events(experiment_id, variants, events)

    assert result is not None
    assert result["variants"]["control"]["visitors"] == 1
    assert result["variants"]["control"]["conversions"] == 1
    assert result["variants"]["treatment"]["visitors"] == 1
    assert result["variants"]["treatment"]["conversions"] == 1
    assert result["variants"]["treatment"]["revenue"] == 42
