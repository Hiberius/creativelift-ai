class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class GoogleAdsMetadataAdapter:
    source = "google_ads"

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        customer_id = config.get("customer_id")
        if not isinstance(customer_id, str) or not customer_id.strip():
            raise ConfigValidationError("config.customer_id is required and must be a non-empty string")
        for optional_field in ("developer_token_secret_ref", "oauth_secret_ref"):
            value = config.get(optional_field)
            if value is not None and not isinstance(value, str):
                raise ConfigValidationError(f"config.{optional_field} must be a string when present")
        allowed_fields = {"customer_id", "developer_token_secret_ref", "oauth_secret_ref"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "GoogleAdsMetadataAdapter.pull is not implemented; push normalized events via the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "ad_metadata",
            "external_id": raw.get("ad_id"),
            "occurred_at": raw.get("updated_at"),
            "payload": raw,
        }
