"""Make the monorepo statistical services importable from a source checkout.

The API imports experiment_engine, bandit_service, uplift_service and
mmm_service. Installed deployments (Docker image, `make setup`, CI) provide
them as packages; this fallback lets `uvicorn app.main:app` work straight
from a fresh clone by adding the sibling `services/*` directories to
``sys.path`` only when the packages are not already installed.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SERVICE_PACKAGES = {
    "experiment_engine": "experiment-engine",
    "bandit_service": "bandit-service",
    "uplift_service": "uplift-service",
    "mmm_service": "mmm-service",
}


def ensure_services_importable() -> None:
    missing = [name for name in _SERVICE_PACKAGES if importlib.util.find_spec(name) is None]
    if not missing:
        return
    for candidate in Path(__file__).resolve().parents:
        services_dir = candidate / "services"
        # The repo-root services/ dir, not the API's own app/services package.
        if not (services_dir / "experiment-engine").is_dir():
            continue
        for package_name in missing:
            package_dir = services_dir / _SERVICE_PACKAGES[package_name]
            if package_dir.is_dir():
                sys.path.insert(0, str(package_dir))
        return


ensure_services_importable()
