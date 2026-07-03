import importlib.util
from pathlib import Path

import pytest

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("google_ads_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
GoogleAdsMetadataAdapter = module.GoogleAdsMetadataAdapter
ConfigValidationError = module.ConfigValidationError


def test_google_ads_normalize() -> None:
    assert GoogleAdsMetadataAdapter().normalize({"ad_id": "ad1"})["record_type"] == "ad_metadata"


def test_google_ads_validate_config_accepts_minimal_config() -> None:
    GoogleAdsMetadataAdapter().validate_config({"customer_id": "123-456-7890"})


def test_google_ads_validate_config_rejects_missing_customer_id() -> None:
    with pytest.raises(ConfigValidationError):
        GoogleAdsMetadataAdapter().validate_config({})


def test_google_ads_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        GoogleAdsMetadataAdapter().validate_config({"customer_id": "123", "unexpected": "nope"})


def test_google_ads_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        GoogleAdsMetadataAdapter().pull()
