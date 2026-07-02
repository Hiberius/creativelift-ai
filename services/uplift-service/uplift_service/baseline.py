from __future__ import annotations

from collections import defaultdict


def score_segment_uplift(rows: list[dict], segment_key: str = "segment") -> list[dict]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: {"treated": [], "control": []})
    for row in rows:
        bucket = buckets[str(row.get(segment_key, "unknown"))]
        outcome = float(row.get("outcome", 0))
        if row.get("treated"):
            bucket["treated"].append(outcome)
        else:
            bucket["control"].append(outcome)
    scores = []
    for segment, values in buckets.items():
        treated = values["treated"]
        control = values["control"]
        treated_rate = sum(treated) / len(treated) if treated else 0.0
        control_rate = sum(control) / len(control) if control else 0.0
        scores.append(
            {
                "segment": segment,
                "treated_rate": treated_rate,
                "control_rate": control_rate,
                "uplift": treated_rate - control_rate,
                "auuc": None,
                "qini": None,
            }
        )
    return sorted(scores, key=lambda item: item["uplift"], reverse=True)
