from connectors.snowplow.src.adapter import SnowplowAdapter


def test_snowplow_normalize() -> None:
    assert SnowplowAdapter().normalize({"event_id": "e1"})["record_type"] == "event"
