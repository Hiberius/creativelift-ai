from mmm_service import run_demo_mmm


def test_demo_mmm_returns_channel_contributions() -> None:
    result = run_demo_mmm(
        [
            {"week": "2026-01-01", "paid_social_spend": 100, "search_spend": 50},
            {"week": "2026-01-08", "paid_social_spend": 100, "search_spend": 150},
        ]
    )
    assert result["status"] == "completed_demo"
    assert set(result["channels"]) == {"paid_social", "search"}
