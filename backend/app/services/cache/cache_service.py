"""
Cache Service - Redis Integration.
"""

import json
from typing import Any, Optional

import redis

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheService:
    """Redis cache service with fallback to in-memory."""

    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
        self._memory_cache: dict[str, Any] = {}
        self._connected = False

    @property
    def redis_client(self) -> Optional[redis.Redis]:
        if self._redis_client is None and settings.redis_enabled:
            try:
                self._redis_client = redis.from_url(
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
        except:
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

    def set(self, key: str, value: Any, ttl: Optional[int] = 3600) -> bool:
        """Set value in cache."""
        try:
            serialized = json.dumps(value)

            if self.redis_client:
                if ttl:
                    self.redis_client.setex(key, ttl, serialized)
                else:
                    self.redis_client.set(key, serialized)

            self._memory_cache[key] = value
            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self._memory_cache[key] = value
            return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            if self.redis_client:
                self.redis_client.delete(key)
            self._memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self.redis_client:
            try:
                return bool(self.redis_client.exists(key))
            except Exception as e:
                logger.error(f"Cache exists error: {e}")

        return key in self._memory_cache

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        count = 0
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)

            keys_to_delete = [
                k for k in self._memory_cache if pattern.replace("*", "") in k
            ]
            for k in keys_to_delete:
                del self._memory_cache[k]
                count += 1

        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")

        return count

    def clear_all(self) -> bool:
        """Clear all cache."""
        try:
            if self.redis_client:
                self.redis_client.flushdb()
            self._memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear all error: {e}")
            return False

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "memory_keys": len(self._memory_cache),
            "redis_connected": self.is_connected(),
        }

        if self.redis_client:
            try:
                info = self.redis_client.info("memory")
                stats["redis_memory"] = info.get("used_memory_human", "N/A")
                stats["redis_keys"] = self.redis_client.dbsize()
            except Exception as e:
                logger.error(f"Redis stats error: {e}")

        return stats


cache_service = CacheService()
