"""
API Key authentication middleware/dependency.
Supports both Bearer token and X-API-Key header formats.
"""

import os
import secrets
from fastapi import HTTPException, Header, Security
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)

# Load from environment
API_KEY = os.getenv("API_KEY", "")

# Support both auth methods
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    x_api_key: Optional[str] = Security(api_key_header),
    bearer: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """
    Verify API key from either:
    - X-API-Key header
    - Authorization: Bearer <token> header
    """
    # If no API key is configured, allow all (dev mode)
    if not API_KEY:
        logger.warning("⚠️  No API_KEY set — running in open mode")
        return "dev-mode"

    # Check X-API-Key header
    if x_api_key and secrets.compare_digest(x_api_key, API_KEY):
        return x_api_key

    # Check Bearer token
    if bearer and secrets.compare_digest(bearer.credentials, API_KEY):
        return bearer.credentials

    logger.warning("Authentication failed: invalid or missing API key")
    raise HTTPException(
        status_code=401,
        detail="Invalid or missing API key. Provide via 'X-API-Key' header or 'Authorization: Bearer <key>'",
        headers={"WWW-Authenticate": "Bearer"},
    )
