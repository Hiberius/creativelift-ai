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


def test_bandit_from_state_restores_persisted_parameters() -> None:
    bandit = ThompsonBandit.from_state(
        {"control": {"alpha": 3.0, "beta": 1.0}, "variant": {"alpha": 1.0, "beta": 4.0}}
    )
    snapshot = bandit.snapshot()
    assert snapshot["control"] == {"alpha": 3.0, "beta": 1.0}
    assert snapshot["variant"] == {"alpha": 1.0, "beta": 4.0}
