from uplift_service import score_segment_uplift


def test_segment_uplift_orders_by_delta() -> None:
    rows = [
        {"segment": "saas", "treated": True, "outcome": 1},
        {"segment": "saas", "treated": False, "outcome": 0},
        {"segment": "dtc", "treated": True, "outcome": 0},
        {"segment": "dtc", "treated": False, "outcome": 1},
    ]
    scores = score_segment_uplift(rows)
    assert scores[0]["segment"] == "saas"
    assert scores[0]["uplift"] > 0
