import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("meta_ads_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
MetaAdsMetadataAdapter = module.MetaAdsMetadataAdapter


def test_meta_ads_normalize() -> None:
    assert MetaAdsMetadataAdapter().normalize({"creative_id": "c1"})["source"] == "meta_ads"
