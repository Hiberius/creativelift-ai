import pytest

from connectors.hubspot.src.adapter import ConfigValidationError, HubSpotAdapter


def test_hubspot_normalize() -> None:
    assert HubSpotAdapter().normalize({"id": "lead1"})["source"] == "hubspot"


def test_hubspot_validate_config_accepts_minimal_config() -> None:
    HubSpotAdapter().validate_config({"portal_id": "12345"})


def test_hubspot_validate_config_rejects_missing_portal_id() -> None:
    with pytest.raises(ConfigValidationError):
        HubSpotAdapter().validate_config({})


def test_hubspot_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        HubSpotAdapter().validate_config({"portal_id": "12345", "unexpected": "nope"})


def test_hubspot_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        HubSpotAdapter().pull()
