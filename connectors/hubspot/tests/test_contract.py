from connectors.hubspot.src.adapter import HubSpotAdapter


def test_hubspot_normalize() -> None:
    assert HubSpotAdapter().normalize({"id": "lead1"})["source"] == "hubspot"
