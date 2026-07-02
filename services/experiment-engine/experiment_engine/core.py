from __future__ import annotations

from dataclasses import dataclass
from math import erf, sqrt


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
) -> dict[str, float | str]:
    if control.visitors < 30 or treatment.visitors < 30:
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


def sequential_peek(current_result: dict, spending_plan: str = "placeholder") -> dict:
    return {
        "status": "not_implemented",
        "spending_plan": spending_plan,
        "message": "Sequential testing boundary scaffold. Add alpha-spending or always-valid inference before production use.",
        "current_result": current_result,
    }
