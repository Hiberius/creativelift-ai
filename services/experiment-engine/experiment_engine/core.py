from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, sqrt


@dataclass(frozen=True)
class VariantStats:
    key: str
    visitors: int
    conversions: int
    revenue: float = 0.0

    @property
    def conversion_rate(self) -> float:
        return self.conversions / self.visitors if self.visitors else 0.0

    @property
    def revenue_per_visitor(self) -> float:
        return self.revenue / self.visitors if self.visitors else 0.0


def normal_cdf(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


def compare_conversion(
    control: VariantStats,
    treatment: VariantStats,
    confidence: float = 0.95,
    min_visitors: int = 30,
) -> dict[str, float | str]:
    if control.visitors < min_visitors or treatment.visitors < min_visitors:
        return {"decision": "needs_more_data"}
    p_control = control.conversion_rate
    p_treatment = treatment.conversion_rate
    pooled = (control.conversions + treatment.conversions) / (
        control.visitors + treatment.visitors
    )
    se = sqrt(max(pooled * (1 - pooled) * (1 / control.visitors + 1 / treatment.visitors), 1e-12))
    diff = p_treatment - p_control
    z = diff / se
    p_value = 2 * (1 - normal_cdf(abs(z)))
    z_crit = 1.96 if confidence == 0.95 else 1.64
    relative_lift = diff / p_control if p_control else 0.0
    decision = "inconclusive"
    if p_value < 1 - confidence and diff > 0:
        decision = "winner"
    if p_value < 1 - confidence and diff < 0:
        decision = "loser"
    return {
        "control_rate": p_control,
        "treatment_rate": p_treatment,
        "absolute_lift": diff,
        "relative_lift": relative_lift,
        "standard_error": se,
        "z_score": z,
        "p_value": p_value,
        "confidence_interval_low": diff - z_crit * se,
        "confidence_interval_high": diff + z_crit * se,
        "revenue_per_visitor_delta": treatment.revenue_per_visitor - control.revenue_per_visitor,
        "decision": decision,
    }


def srm_check(observed: dict[str, int], expected_allocation: dict[str, float], alpha: float = 0.001) -> dict:
    total = sum(observed.values())
    if total == 0:
        return {"chi_square": 0.0, "p_value": 1.0, "passed": False}
    chi_square = 0.0
    for key, allocation in expected_allocation.items():
        expected = total * allocation
        if expected <= 0:
            continue
        chi_square += (observed.get(key, 0) - expected) ** 2 / expected
    p_value = 1 - erf(sqrt(chi_square / 2))
    return {"chi_square": chi_square, "p_value": p_value, "passed": p_value >= alpha}


def cuped_adjust(outcome: list[float], pre_experiment_covariate: list[float]) -> list[float]:
    if len(outcome) != len(pre_experiment_covariate):
        raise ValueError("outcome and pre_experiment_covariate must have the same length")
    if not outcome:
        return []
    x_mean = sum(pre_experiment_covariate) / len(pre_experiment_covariate)
    y_mean = sum(outcome) / len(outcome)
    cov_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(pre_experiment_covariate, outcome))
    var_x = sum((x - x_mean) ** 2 for x in pre_experiment_covariate)
    theta = cov_xy / var_x if var_x else 0.0
    return [y - theta * (x - x_mean) for y, x in zip(outcome, pre_experiment_covariate)]


def sequential_peek(
    control: VariantStats,
    treatment: VariantStats,
    alpha: float = 0.05,
    mixture_sd: float = 0.01,
) -> dict:
    """Always-valid sequential test for the difference in conversion rates.

    Implements the mixture sequential probability ratio test (mSPRT) with a
    zero-centered normal mixing distribution N(0, mixture_sd**2) over the
    treatment-minus-control conversion-rate difference, using the standard
    normal approximation for two-sample binomial data. The reciprocal of the
    mixture likelihood ratio is an always-valid p-value: it can be inspected
    after every new observation ("peeking") while keeping the type I error at
    or below ``alpha`` uniformly over time.

    Reference: Johari, Koomen, Pekelis & Walsh, "Peeking at A/B Tests: Why It
    Matters, and What to Do About It", KDD 2017 (normal-mixture mSPRT).

    ``mixture_sd`` is the prior scale of plausible effects on the absolute
    conversion-rate-difference scale; the default of 0.01 (one percentage
    point) suits typical conversion experiments.
    """
    header = {
        "method": "msprt_normal_mixture",
        "alpha": alpha,
        "mixture_sd": mixture_sd,
    }
    if control.visitors <= 0 or treatment.visitors <= 0:
        return header | {
            "observed_effect": 0.0,
            "log_likelihood_ratio": 0.0,
            "always_valid_p_value": 1.0,
            "can_stop": False,
            "decision": "continue",
            "message": "Both variants need visitors before sequential monitoring can run.",
        }
    pooled = (control.conversions + treatment.conversions) / (
        control.visitors + treatment.visitors
    )
    variance = max(pooled * (1 - pooled) * (1 / control.visitors + 1 / treatment.visitors), 1e-12)
    effect = treatment.conversion_rate - control.conversion_rate
    tau_squared = mixture_sd**2
    log_likelihood_ratio = 0.5 * log(variance / (variance + tau_squared)) + (
        effect**2 * tau_squared / (2 * variance * (variance + tau_squared))
    )
    # Work in log space: exp(-llr) underflows to 0.0 for decisive tests
    # instead of overflowing the direct likelihood ratio.
    always_valid_p_value = min(1.0, exp(-log_likelihood_ratio))
    can_stop = always_valid_p_value <= alpha
    return header | {
        "observed_effect": effect,
        "log_likelihood_ratio": log_likelihood_ratio,
        "always_valid_p_value": always_valid_p_value,
        "can_stop": can_stop,
        "decision": "stop" if can_stop else "continue",
    }
