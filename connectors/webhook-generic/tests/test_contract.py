import importlib.util
from pathlib import Path

import pytest

module_path = Path(__file__).resolve().parents[1] / "src" / "adapter.py"
spec = importlib.util.spec_from_file_location("webhook_generic_adapter", module_path)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
GenericWebhookAdapter = module.GenericWebhookAdapter
ConfigValidationError = module.ConfigValidationError


def test_webhook_normalize() -> None:
    adapter = GenericWebhookAdapter({"event_name_path": "type", "timestamp_path": "ts"})
    assert adapter.normalize({"type": "purchase", "ts": "2026-06-28T00:00:00Z"})["source"] == "webhook_generic"


def test_webhook_validate_config_accepts_minimal_config() -> None:
    adapter = GenericWebhookAdapter()
    adapter.validate_config({"event_name_path": "type", "timestamp_path": "ts"})


def test_webhook_validate_config_rejects_missing_required_paths() -> None:
    adapter = GenericWebhookAdapter()
    with pytest.raises(ConfigValidationError):
        adapter.validate_config({"event_name_path": "type"})


def test_webhook_validate_config_rejects_unknown_fields() -> None:
    adapter = GenericWebhookAdapter()
    with pytest.raises(ConfigValidationError):
        adapter.validate_config(
            {"event_name_path": "type", "timestamp_path": "ts", "unexpected": "nope"}
        )


def test_webhook_pull_is_not_implemented() -> None:
    with pytest.raises(NotImplementedError):
        GenericWebhookAdapter({"event_name_path": "type", "timestamp_path": "ts"}).pull()
