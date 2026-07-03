"""Redis-backed rate limiter: fixed window, 429s, and in-memory fallback."""

import pytest
from fastapi import HTTPException

from app.core.rate_limit import RedisRateLimiter


class _FakeRedis:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}
        self.ttls: dict[str, int] = {}

    def incr(self, key: str) -> int:
        self.counters[key] = self.counters.get(key, 0) + 1
        return self.counters[key]

    def expire(self, key: str, seconds: int) -> None:
        self.ttls[key] = seconds

    def ttl(self, key: str) -> int:
        return self.ttls.get(key, 1)


class _BrokenRedis:
    def incr(self, key: str) -> int:
        raise ConnectionError("redis down")


def test_redis_limiter_allows_up_to_limit_then_429():
    limiter = RedisRateLimiter("redis://unused", client=_FakeRedis())
    for _ in range(3):
        limiter.check("client-a", 3, 60)
    with pytest.raises(HTTPException) as excinfo:
        limiter.check("client-a", 3, 60)
    assert excinfo.value.status_code == 429
    assert excinfo.value.detail["retry_after_seconds"] >= 1


def test_redis_limiter_isolates_keys():
    limiter = RedisRateLimiter("redis://unused", client=_FakeRedis())
    for _ in range(3):
        limiter.check("client-a", 3, 60)
    # A different caller still has full quota.
    limiter.check("client-b", 3, 60)


def test_redis_limiter_falls_back_to_memory_when_redis_is_down():
    limiter = RedisRateLimiter("redis://unused", client=_BrokenRedis())
    for _ in range(2):
        limiter.check("client-c", 2, 60)
    # The in-memory fallback still enforces the limit.
    with pytest.raises(HTTPException) as excinfo:
        limiter.check("client-c", 2, 60)
    assert excinfo.value.status_code == 429
