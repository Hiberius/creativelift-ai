class RudderAdapter:
    source = "rudder"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": raw.get("type", "event"),
            "external_id": raw.get("messageId"),
            "occurred_at": raw.get("timestamp"),
            "payload": raw,
        }
