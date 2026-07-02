from __future__ import annotations

from dataclasses import dataclass
from time import time

from fastapi import HTTPException, Request, status

from app.core.config import settings


@dataclass
class Bucket:
    limit: int
    window_seconds: int
    reset_at: float
    count: int = 0


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._buckets: dict[str, Bucket] = {}

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        now = time()
        bucket = self._buckets.get(key)
        if bucket is None or now >= bucket.reset_at:
            self._buckets[key] = Bucket(limit=limit, window_seconds=window_seconds, reset_at=now + window_seconds, count=1)
            return
        bucket.count += 1
        if bucket.count > limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "rate_limited", "retry_after_seconds": int(bucket.reset_at - now)},
            )


rate_limiter = InMemoryRateLimiter()


async def enforce_rate_limit(request: Request) -> None:
    identifier = (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization")
        or request.headers.get("X-Forwarded-For")
        or (request.client.host if request.client else "unknown")
    )
    rate_limiter.check(identifier, settings.rate_limit_requests, settings.rate_limit_window_seconds)
