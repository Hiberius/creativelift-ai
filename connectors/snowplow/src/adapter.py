class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class SnowplowAdapter:
    source = "snowplow"

    _ALLOWED_WAREHOUSES = {"bigquery", "snowflake", "redshift"}

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        warehouse = config.get("warehouse")
        if not isinstance(warehouse, str) or warehouse not in self._ALLOWED_WAREHOUSES:
            raise ConfigValidationError(
                f"config.warehouse is required and must be one of {sorted(self._ALLOWED_WAREHOUSES)}"
            )
        events_table = config.get("events_table")
        if events_table is not None and not isinstance(events_table, str):
            raise ConfigValidationError("config.events_table must be a string when present")
        allowed_fields = {"warehouse", "events_table"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "SnowplowAdapter.pull is not implemented; push normalized events via the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "event",
            "external_id": raw.get("event_id"),
            "occurred_at": raw.get("collector_tstamp"),
            "payload": raw,
        }
