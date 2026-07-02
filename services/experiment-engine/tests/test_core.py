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


def test_sequential_placeholder_is_explicit() -> None:
    assert sequential_peek({"p_value": 0.12})["status"] == "not_implemented"
