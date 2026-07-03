import pytest

from connectors.rudder.src.adapter import ConfigValidationError, RudderAdapter


def test_rudder_normalize() -> None:
    assert RudderAdapter().normalize({"messageId": "m1"})["source"] == "rudder"


def test_rudder_validate_config_accepts_minimal_config() -> None:
    RudderAdapter().validate_config({"write_key": "wk_123"})


def test_rudder_validate_config_rejects_missing_write_key() -> None:
    with pytest.raises(ConfigValidationError):
        RudderAdapter().validate_config({})


def test_rudder_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        RudderAdapter().validate_config({"write_key": "wk_123", "unexpected": "nope"})


def test_rudder_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        RudderAdapter().pull()
