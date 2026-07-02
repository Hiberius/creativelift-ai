from __future__ import annotations


def run_demo_mmm(weekly_rows: list[dict]) -> dict:
    if not weekly_rows:
        return {"status": "empty", "channels": {}}
    channels = [key for key in weekly_rows[0] if key.endswith("_spend")]
    totals = {channel.replace("_spend", ""): sum(float(row.get(channel, 0)) for row in weekly_rows) for channel in channels}
    total_spend = sum(totals.values()) or 1.0
    contributions = {channel: spend / total_spend for channel, spend in totals.items()}
    return {
        "status": "completed_demo",
        "channels": contributions,
        "calibration_note": "Use CreativeLift experiment lift estimates as calibration priors in future Bayesian MMM.",
        "adapters": ["PyMC-Marketing", "Meridian", "Robyn"],
    }
