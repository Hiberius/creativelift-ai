from __future__ import annotations

import json
import logging
from typing import Any


logger = logging.getLogger("creativelift")
logging.basicConfig(level=logging.INFO)


def log_event(event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **fields}, default=str, sort_keys=True))
