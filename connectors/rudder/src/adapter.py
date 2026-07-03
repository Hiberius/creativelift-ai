class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class RudderAdapter:
    source = "rudder"

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        write_key = config.get("write_key")
        if not isinstance(write_key, str) or not write_key.strip():
            raise ConfigValidationError("config.write_key is required and must be a non-empty string")
        data_plane_url = config.get("data_plane_url")
        if data_plane_url is not None and not isinstance(data_plane_url, str):
            raise ConfigValidationError("config.data_plane_url must be a string when present")
        allowed_fields = {"write_key", "data_plane_url"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "RudderAdapter.pull is not implemented; push normalized events via the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": raw.get("type", "event"),
            "external_id": raw.get("messageId"),
            "occurred_at": raw.get("timestamp"),
            "payload": raw,
        }
