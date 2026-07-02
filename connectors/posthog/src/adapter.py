class PostHogAdapter:
    source = "posthog"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "event",
            "external_id": raw.get("uuid") or raw.get("event"),
            "occurred_at": raw.get("timestamp"),
            "payload": raw,
        }
