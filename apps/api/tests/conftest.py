from collections.abc import Generator
import os
from pathlib import Path

os.environ.setdefault(
    "CREATIVELIFT_REPORT_STORE",
    str(Path(__file__).resolve().parents[3] / "tmp" / "test_measurement_reports.json"),
)

import pytest
from fastapi.testclient import TestClient

from app.core.security import reset_demo_organization_id
from app.main import create_app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    reset_demo_organization_id()
    with TestClient(create_app()) as test_client:
        yield test_client


@pytest.fixture
def api_headers() -> dict[str, str]:
    return {"X-API-Key": "dev-api-key"}
