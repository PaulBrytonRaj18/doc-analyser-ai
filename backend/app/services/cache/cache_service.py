"""
Cache Service - Redis Integration (Optional).
"""

import json
from typing import Any, Optional

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import for optional dependencies
_redis = None


def _get_redis():
    global _redis
    if _redis is None:
        try:
            import redis

            _redis = redis
        except ImportError:
            logger.warning("Redis not installed. Using in-memory cache.")
            _redis = False
    return _redis


class CacheService:
    """Redis cache service with fallback to in-memory."""

    def __init__(self):
        self._redis_client = None
        self._memory_cache: dict = {}
        self._connected = False
        self._checked = False

    @property
    def redis_client(self):
        if self._checked:
            return self._redis_client

        self._checked = True
        if not settings.redis_enabled:
            return None

        redis_lib = _get_redis()
        if not redis_lib:
            return None

        try:
            self._redis_client = redis_lib.from_url(
                settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            self._redis_client.ping()
            self._connected = True
            logger.info("Redis cache connected")
        except Exception as e:
            logger.warning(f"Redis not available: {e}. Using in-memory cache.")
            self._connected = False
            self._redis_client = None

        return self._redis_client

    def is_connected(self) -> bool:
        if not self.redis_client:
            return False
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.error(f"Redis get error: {e}")

        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        if self.redis_client:
            try:
                serialized = json.dumps(value)
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)
                return True
            except Exception as e:
                logger.error(f"Redis set error: {e}")

        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete error: {e}")

        self._memory_cache.pop(key, None)
        return True

    def clear(self) -> bool:
        """Clear all cache."""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
                return True
            except Exception as e:
                logger.error(f"Redis clear error: {e}")

        self._memory_cache.clear()
        return True

    def get_many(self, keys: list[str]) -> dict[str, Any]:
        """Get multiple values from cache."""
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, mapping: dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        for key, value in mapping.items():
            self.set(key, value, ttl)
        return True


cache_service = CacheService()
