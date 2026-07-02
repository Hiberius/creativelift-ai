from connectors.rudder.src.adapter import RudderAdapter


def test_rudder_normalize() -> None:
    assert RudderAdapter().normalize({"messageId": "m1"})["source"] == "rudder"
