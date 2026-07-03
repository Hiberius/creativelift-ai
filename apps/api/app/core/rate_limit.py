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


class RedisRateLimiter:
    """Fixed-window limiter on Redis so limits hold across API replicas.

    Falls back to the in-memory limiter if Redis is unreachable, so a Redis
    outage degrades to per-process limiting instead of dropping traffic.
    """

    def __init__(self, redis_url: str, client: object | None = None) -> None:
        self._redis_url = redis_url
        self._client = client
        self._fallback = InMemoryRateLimiter()
        self._warned = False

    def _get_client(self):
        if self._client is None:
            import redis

            self._client = redis.Redis.from_url(self._redis_url, socket_timeout=1)
        return self._client

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        window = int(time() // window_seconds)
        redis_key = f"ratelimit:{key}:{window}"
        try:
            client = self._get_client()
            count = client.incr(redis_key)
            if count == 1:
                client.expire(redis_key, window_seconds)
        except Exception:
            if not self._warned:
                from app.core.logging import logger

                logger.warning("Redis rate limiter unavailable; falling back to in-memory")
                self._warned = True
            self._fallback.check(key, limit, window_seconds)
            return
        if count > limit:
            ttl = client.ttl(redis_key)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"error": "rate_limited", "retry_after_seconds": max(int(ttl), 1)},
            )


def create_rate_limiter():
    if settings.rate_limit_backend == "redis":
        return RedisRateLimiter(settings.redis_url)
    return InMemoryRateLimiter()


rate_limiter = create_rate_limiter()


async def enforce_rate_limit(request: Request) -> None:
    identifier = (
        request.headers.get("X-API-Key")
        or request.headers.get("Authorization")
        or request.headers.get("X-Forwarded-For")
        or (request.client.host if request.client else "unknown")
    )
    rate_limiter.check(identifier, settings.rate_limit_requests, settings.rate_limit_window_seconds)
