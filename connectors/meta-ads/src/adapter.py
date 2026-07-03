class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class MetaAdsMetadataAdapter:
    source = "meta_ads"

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        ad_account_id = config.get("ad_account_id")
        if not isinstance(ad_account_id, str) or not ad_account_id.strip():
            raise ConfigValidationError("config.ad_account_id is required and must be a non-empty string")
        access_token_secret_ref = config.get("access_token_secret_ref")
        if access_token_secret_ref is not None and not isinstance(access_token_secret_ref, str):
            raise ConfigValidationError("config.access_token_secret_ref must be a string when present")
        allowed_fields = {"ad_account_id", "access_token_secret_ref"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "MetaAdsMetadataAdapter.pull is not implemented; push normalized events via the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "ad_metadata",
            "external_id": raw.get("creative_id") or raw.get("ad_id"),
            "occurred_at": raw.get("updated_time"),
            "payload": raw,
        }
