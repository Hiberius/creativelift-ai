import pytest

from connectors.snowplow.src.adapter import ConfigValidationError, SnowplowAdapter


def test_snowplow_normalize() -> None:
    assert SnowplowAdapter().normalize({"event_id": "e1"})["record_type"] == "event"


def test_snowplow_validate_config_accepts_minimal_config() -> None:
    SnowplowAdapter().validate_config({"warehouse": "bigquery"})


def test_snowplow_validate_config_rejects_missing_warehouse() -> None:
    with pytest.raises(ConfigValidationError):
        SnowplowAdapter().validate_config({})


def test_snowplow_validate_config_rejects_unsupported_warehouse() -> None:
    with pytest.raises(ConfigValidationError):
        SnowplowAdapter().validate_config({"warehouse": "not-a-warehouse"})


def test_snowplow_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        SnowplowAdapter().validate_config({"warehouse": "bigquery", "unexpected": "nope"})


def test_snowplow_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        SnowplowAdapter().pull()
