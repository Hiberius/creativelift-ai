class HubSpotAdapter:
    source = "hubspot"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": raw.get("objectType", "lead"),
            "external_id": raw.get("id"),
            "occurred_at": raw.get("updatedAt"),
            "payload": raw,
        }
