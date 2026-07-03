class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


def get_path(payload: dict, dotted_path: str) -> object:
    current: object = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


class GenericWebhookAdapter:
    source = "webhook_generic"

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self.mapping = mapping or {}

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        for required_field in ("event_name_path", "timestamp_path"):
            value = config.get(required_field)
            if not isinstance(value, str) or not value.strip():
                raise ConfigValidationError(f"config.{required_field} is required and must be a non-empty string")
        for optional_field in ("anonymous_id_path", "user_id_path"):
            value = config.get(optional_field)
            if value is not None and not isinstance(value, str):
                raise ConfigValidationError(f"config.{optional_field} must be a string when present")
        allowed_fields = {"event_name_path", "timestamp_path", "anonymous_id_path", "user_id_path"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "GenericWebhookAdapter.pull is not implemented; webhook-generic is push-only, "
            "post raw payloads to the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "event",
            "external_id": raw.get("id"),
            "occurred_at": get_path(raw, self.mapping["timestamp_path"]),
            "payload": {
                "event_name": get_path(raw, self.mapping["event_name_path"]),
                "anonymous_id": get_path(raw, self.mapping.get("anonymous_id_path", "")),
                "user_id": get_path(raw, self.mapping.get("user_id_path", "")),
                "properties": raw,
            },
        }
