from bandit_service import ThompsonBandit


def test_bandit_updates_successes() -> None:
    bandit = ThompsonBandit(["control", "variant"])
    bandit.update("variant", True)
    assert bandit.snapshot()["variant"]["alpha"] == 2.0


def test_bandit_decision_returns_known_arm() -> None:
    bandit = ThompsonBandit(["control", "variant"])
    chosen, samples = bandit.decide()
    assert chosen in samples
    assert set(samples) == {"control", "variant"}
