from __future__ import annotations

from dataclasses import dataclass
from random import betavariate


@dataclass
class ArmState:
    alpha: float = 1.0
    beta: float = 1.0


class ThompsonBandit:
    def __init__(self, arms: list[str]) -> None:
        if len(arms) < 2:
            raise ValueError("At least two arms are required")
        self.arms = {arm: ArmState() for arm in arms}

    @classmethod
    def from_state(cls, arms: dict[str, dict[str, float]]) -> ThompsonBandit:
        """Rebuild a bandit from persisted per-arm Beta parameters."""
        bandit = cls(list(arms))
        for arm, state in arms.items():
            bandit.arms[arm] = ArmState(
                alpha=float(state.get("alpha", 1.0)),
                beta=float(state.get("beta", 1.0)),
            )
        return bandit

    def decide(self) -> tuple[str, dict[str, float]]:
        samples = {arm: betavariate(state.alpha, state.beta) for arm, state in self.arms.items()}
        return max(samples, key=samples.get), samples

    def update(self, arm: str, success: bool) -> None:
        if arm not in self.arms:
            raise KeyError(f"Unknown arm: {arm}")
        if success:
            self.arms[arm].alpha += 1
        else:
            self.arms[arm].beta += 1

    def snapshot(self) -> dict[str, dict[str, float]]:
        return {arm: state.__dict__.copy() for arm, state in self.arms.items()}
