import importlib.util
from pathlib import Path

import pytest

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("meta_ads_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
MetaAdsMetadataAdapter = module.MetaAdsMetadataAdapter
ConfigValidationError = module.ConfigValidationError


def test_meta_ads_normalize() -> None:
    assert MetaAdsMetadataAdapter().normalize({"creative_id": "c1"})["source"] == "meta_ads"


def test_meta_ads_validate_config_accepts_minimal_config() -> None:
    MetaAdsMetadataAdapter().validate_config({"ad_account_id": "act_123"})


def test_meta_ads_validate_config_rejects_missing_ad_account_id() -> None:
    with pytest.raises(ConfigValidationError):
        MetaAdsMetadataAdapter().validate_config({})


def test_meta_ads_validate_config_rejects_unknown_fields() -> None:
    with pytest.raises(ConfigValidationError):
        MetaAdsMetadataAdapter().validate_config({"ad_account_id": "act_123", "unexpected": "nope"})


def test_meta_ads_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        MetaAdsMetadataAdapter().pull()
