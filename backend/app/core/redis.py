"""Redis caching layer for telemetry data.

If REDIS_URL is not configured, all cache operations gracefully no-op.
"""

import json
import logging
from typing import Optional

import redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_client: Optional[redis.Redis] = None
_initialized = False


def _get_redis() -> Optional[redis.Redis]:
    """Lazy-initialize Redis connection. Returns None if unavailable."""
    global _redis_client, _initialized
    if _initialized:
        return _redis_client

    _initialized = True
    settings = get_settings()
    if not settings.REDIS_URL:
        logger.info("REDIS_URL not set -- caching disabled")
        return None

    try:
        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL, decode_responses=True, socket_timeout=2
        )
        _redis_client.ping()
        logger.info("Redis connected at %s", settings.REDIS_URL)
    except Exception as exc:
        logger.warning("Redis unavailable (%s) -- caching disabled", exc)
        _redis_client = None

    return _redis_client


def cache_latest_telemetry(machine_id: str, payload: dict, ttl: int = 60) -> None:
    """Cache the latest telemetry reading for a machine with a TTL."""
    client = _get_redis()
    if client is None:
        return
    try:
        client.setex(f"telemetry:latest:{machine_id}", ttl, json.dumps(payload))
    except Exception as exc:
        logger.warning("Redis SET failed: %s", exc)


def get_cached_telemetry(machine_id: str) -> Optional[dict]:
    """Return cached telemetry for a machine, or None on miss."""
    client = _get_redis()
    if client is None:
        return None
    try:
        data = client.get(f"telemetry:latest:{machine_id}")
        return json.loads(data) if data else None
    except Exception as exc:
        logger.warning("Redis GET failed: %s", exc)
        return None


def cache_diagnosis(machine_id: str, diagnosis: dict, ttl: int = 300) -> None:
    """Cache the latest diagnosis for a machine."""
    client = _get_redis()
    if client is None:
        return
    try:
        client.setex(f"diagnosis:latest:{machine_id}", ttl, json.dumps(diagnosis))
    except Exception as exc:
        logger.warning("Redis SET failed: %s", exc)
