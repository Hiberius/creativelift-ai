class GoogleAdsMetadataAdapter:
    source = "google_ads"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "ad_metadata",
            "external_id": raw.get("ad_id"),
            "occurred_at": raw.get("updated_at"),
            "payload": raw,
        }
