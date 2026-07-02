import importlib.util
from pathlib import Path

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("webhook_generic_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
GenericWebhookAdapter = module.GenericWebhookAdapter


def test_webhook_normalize() -> None:
    adapter = GenericWebhookAdapter({"event_name_path": "type", "timestamp_path": "ts"})
    assert adapter.normalize({"type": "purchase", "ts": "2026-06-28T00:00:00Z"})["source"] == "webhook_generic"
