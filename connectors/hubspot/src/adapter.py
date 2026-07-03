class ConfigValidationError(ValueError):
    """Raised when a connector configuration fails schema validation."""


class HubSpotAdapter:
    source = "hubspot"

    def validate_config(self, config: dict) -> None:
        if not isinstance(config, dict):
            raise ConfigValidationError("config must be an object")
        portal_id = config.get("portal_id")
        if not isinstance(portal_id, str) or not portal_id.strip():
            raise ConfigValidationError("config.portal_id is required and must be a non-empty string")
        private_app_token_secret_ref = config.get("private_app_token_secret_ref")
        if private_app_token_secret_ref is not None and not isinstance(private_app_token_secret_ref, str):
            raise ConfigValidationError("config.private_app_token_secret_ref must be a string when present")
        allowed_fields = {"portal_id", "private_app_token_secret_ref"}
        unknown_fields = set(config) - allowed_fields
        if unknown_fields:
            raise ConfigValidationError(f"config has unknown fields: {sorted(unknown_fields)}")

    def pull(self, since: str | None = None) -> list[dict]:
        raise NotImplementedError(
            "HubSpotAdapter.pull is not implemented; push normalized events via the sync API instead"
        )

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": raw.get("objectType", "lead"),
            "external_id": raw.get("id"),
            "occurred_at": raw.get("updatedAt"),
            "payload": raw,
        }
