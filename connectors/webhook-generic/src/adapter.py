def get_path(payload: dict, dotted_path: str) -> object:
    current: object = payload
    for part in dotted_path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    return current


class GenericWebhookAdapter:
    source = "webhook_generic"

    def __init__(self, mapping: dict[str, str]) -> None:
        self.mapping = mapping

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
