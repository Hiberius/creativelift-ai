from experiment_engine import VariantStats, compare_conversion, cuped_adjust, srm_check, sequential_peek


def test_compare_conversion_winner() -> None:
    result = compare_conversion(
        VariantStats("control", 20_000, 1_000, 150_000),
        VariantStats("variant", 20_000, 1_250, 205_000),
    )
    assert result["decision"] == "winner"
    assert result["relative_lift"] > 0


def test_srm_check_pass_and_fail() -> None:
    assert srm_check({"a": 5000, "b": 5010}, {"a": 0.5, "b": 0.5})["passed"] is True
    assert srm_check({"a": 9000, "b": 1000}, {"a": 0.5, "b": 0.5})["passed"] is False


def test_cuped_adjust_validates_length() -> None:
    adjusted = cuped_adjust([2, 4, 6], [1, 2, 3])
    assert len(adjusted) == 3


def test_sequential_peek_null_effect_does_not_stop() -> None:
    result = sequential_peek(
        VariantStats("control", 10_000, 500),
        VariantStats("variant", 10_000, 500),
    )
    assert result["method"] == "msprt_normal_mixture"
    assert result["always_valid_p_value"] == 1.0
    assert result["can_stop"] is False
    assert result["decision"] == "continue"


def test_sequential_peek_strong_effect_stops() -> None:
    result = sequential_peek(
        VariantStats("control", 10_000, 500),
        VariantStats("variant", 10_000, 800),
    )
    assert result["always_valid_p_value"] < 0.05
    assert result["can_stop"] is True
    assert result["decision"] == "stop"
    assert result["observed_effect"] > 0


def test_sequential_peek_small_sample_noise_does_not_stop() -> None:
    # A large observed lift on a tiny sample must not trigger an early stop.
    result = sequential_peek(
        VariantStats("control", 20, 1),
        VariantStats("variant", 20, 5),
    )
    assert result["can_stop"] is False


def test_sequential_peek_requires_visitors() -> None:
    result = sequential_peek(
        VariantStats("control", 0, 0),
        VariantStats("variant", 0, 0),
    )
    assert result["always_valid_p_value"] == 1.0
    assert result["can_stop"] is False
