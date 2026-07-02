import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("google_ads_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
GoogleAdsMetadataAdapter = module.GoogleAdsMetadataAdapter


def test_google_ads_normalize() -> None:
    assert GoogleAdsMetadataAdapter().normalize({"ad_id": "ad1"})["record_type"] == "ad_metadata"
