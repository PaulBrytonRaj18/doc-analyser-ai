"""
Security Utilities for API Authentication.
"""

import secrets
import hashlib
import time
from typing import Optional

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = {}

    def check_rate_limit(self, client_id: str) -> tuple[bool, Optional[int]]:
        """Check if client is within rate limit. Returns (allowed, retry_after)."""
        now = time.time()
        window_start = now - self.window_seconds

        if client_id not in self._requests:
            self._requests[client_id] = []

        self._requests[client_id] = [
            ts for ts in self._requests[client_id] if ts > window_start
        ]

        if len(self._requests[client_id]) >= self.max_requests:
            oldest = min(self._requests[client_id])
            retry_after = int(oldest + self.window_seconds - now) + 1
            return False, retry_after

        self._requests[client_id].append(now)
        return True, None


rate_limiter = RateLimiter(
    max_requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds,
)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """Verify API key authentication."""
    if not settings.is_authentication_enabled:
        return "dev_user"

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    if not secrets.compare_digest(api_key, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return "authenticated_user"


def check_rate_limit(client_id: str) -> None:
    """Check rate limit and raise exception if exceeded."""
    allowed, retry_after = rate_limiter.check_rate_limit(client_id)

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={"Retry-After": str(retry_after)},
        )


def generate_api_key() -> str:
    """Generate a secure random API key."""
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()
