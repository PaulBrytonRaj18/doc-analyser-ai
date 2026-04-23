"""
Webhook Dispatcher Service - DocuLens AI v4.0
Handles event dispatching with HMAC-SHA256 signing and retry logic.
"""

import asyncio
import hashlib
import hmac
import json
import time
from datetime import datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.db import Webhook

logger = get_logger(__name__)

WEBHOOK_EVENTS = [
    "document.ready",
    "batch.complete",
    "batch.partial",
    "rag.query.done",
    "document.failed",
]

RETRY_BASE_DELAY = 2.0


class RetryState:
    def __init__(self, max_attempts: int | None = None):
        self.max_attempts = max_attempts or settings.webhook_retry_attempts
        self.current_attempt = 0
        self.last_error: str | None = None
        self.delays: list[float] = []

    @property
    def should_retry(self) -> bool:
        return self.current_attempt < self.max_attempts

    def record_attempt(self, delay: float, error: str | None = None) -> None:
        self.current_attempt += 1
        self.delays.append(delay)
        self.last_error = error

    def reset(self) -> None:
        self.current_attempt = 0
        self.last_error = None
        self.delays = []

    def get_backoff_delay(self) -> float:
        return RETRY_BASE_DELAY ** self.current_attempt


class WebhookDispatcher:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.secret = settings.webhook_secret

    def sign_payload(self, payload: dict[str, Any], timestamp: str) -> str:
        payload_str = json.dumps(payload, sort_keys=True)
        signature_base = f"{timestamp}.{payload_str}"
        signature = hmac.new(
            self.secret.encode("utf-8"),
            signature_base.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"

    def _build_headers(
        self, payload: dict[str, Any], webhook_secret: str | None = None
    ) -> dict[str, str]:
        timestamp = str(int(time.time()))
        secret = webhook_secret or self.secret
        payload_str = json.dumps(payload, sort_keys=True)
        signature_base = f"{timestamp}.{payload_str}"
        signature = hmac.new(
            secret.encode("utf-8"),
            signature_base.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return {
            "Content-Type": "application/json",
            "X-Webhook-Signature": f"sha256={signature}",
            "X-Webhook-Timestamp": timestamp,
            "X-Webhook-Event": payload.get("event", "unknown"),
        }

    async def dispatch(
        self,
        event: str,
        data: dict[str, Any],
        webhook_ids: list[UUID] | None = None,
    ) -> dict[str, Any]:
        if event not in WEBHOOK_EVENTS:
            logger.warning(f"Unknown webhook event: {event}")
            return {"status": "error", "message": f"Unknown event: {event}"}

        query = select(Webhook).where(Webhook.active == True)
        if webhook_ids:
            query = query.where(Webhook.id.in_(webhook_ids))
        else:
            query = query.where(Webhook.events.contains(event))

        result = await self.db.execute(query)
        webhooks = result.scalars().all()

        if not webhooks:
            logger.debug(f"No webhooks configured for event: {event}")
            return {"status": "skipped", "message": "No matching webhooks"}

        payload = {
            "event": event,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": data,
        }

        dispatch_results = []
        for webhook in webhooks:
            dispatch_results.append(
                await self._dispatch_with_retry(webhook, payload)
            )

        success_count = sum(1 for r in dispatch_results if r["success"])
        return {
            "status": "completed",
            "total": len(dispatch_results),
            "successful": success_count,
            "failed": len(dispatch_results) - success_count,
            "results": dispatch_results,
        }

    async def _dispatch_with_retry(
        self, webhook: Webhook, payload: dict[str, Any]
    ) -> dict[str, Any]:
        retry_state = RetryState()
        webhook_secret = webhook.secret if webhook.secret != self.secret else None

        while retry_state.should_retry:
            delay = retry_state.get_backoff_delay()
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = self._build_headers(payload, webhook_secret)
                    response = await client.post(webhook.url, json=payload, headers=headers)

                    if response.is_success:
                        await self._update_webhook_status(webhook, success=True)
                        return {
                            "webhook_id": str(webhook.id),
                            "success": True,
                            "status_code": response.status_code,
                            "attempts": retry_state.current_attempt + 1,
                            "delays": retry_state.delays,
                        }

                    retry_state.record_attempt(delay, f"HTTP {response.status_code}")
                    logger.warning(
                        f"Webhook {webhook.id} failed with {response.status_code}, "
                        f"retry {retry_state.current_attempt}/{retry_state.max_attempts}"
                    )

            except Exception as e:
                retry_state.record_attempt(delay, str(e))
                logger.warning(
                    f"Webhook {webhook.id} error: {e}, "
                    f"retry {retry_state.current_attempt}/{retry_state.max_attempts}"
                )

            if retry_state.should_retry:
                await asyncio.sleep(delay)

        await self._update_webhook_status(webhook, success=False)
        return {
            "webhook_id": str(webhook.id),
            "success": False,
            "attempts": retry_state.current_attempt,
            "delays": retry_state.delays,
            "last_error": retry_state.last_error,
        }

    async def _update_webhook_status(
        self, webhook: Webhook, success: bool
    ) -> None:
        webhook.last_triggered = datetime.utcnow()
        webhook.retry_count = 0 if success else webhook.retry_count + 1
        await self.db.commit()