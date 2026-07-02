class MetaAdsMetadataAdapter:
    source = "meta_ads"

    def normalize(self, raw: dict) -> dict:
        return {
            "source": self.source,
            "record_type": "ad_metadata",
            "external_id": raw.get("creative_id") or raw.get("ad_id"),
            "occurred_at": raw.get("updated_time"),
            "payload": raw,
        }
