import re
from pathlib import Path

from app.main import app


def test_api_reference_lists_every_v1_route():
    docs = Path(__file__).resolve().parents[3] / "docs" / "api-reference.md"
    documented = set(re.findall(r"- `(DELETE|GET|POST|PUT|PATCH) (/v1[^`]+)`", docs.read_text()))

    actual = set()
    for route in app.routes:
        path = getattr(route, "path", "")
        if not path.startswith("/v1"):
            continue
        for method in getattr(route, "methods", set()):
            if method not in {"DELETE", "GET", "POST", "PUT", "PATCH"}:
                continue
            actual.add((method, path))

    assert actual - documented == set()
