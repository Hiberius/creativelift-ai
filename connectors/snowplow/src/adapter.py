class SnowplowAdapter:
    source = "snowplow"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "event",
            "external_id": raw.get("event_id"),
            "occurred_at": raw.get("collector_tstamp"),
            "payload": raw,
        }
