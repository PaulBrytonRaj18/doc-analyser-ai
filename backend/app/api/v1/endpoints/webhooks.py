"""
Webhook API Endpoints - DocuLens AI v4.0
"""

import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.core.security import verify_api_key
from app.models.schemas import (
    WebhookRegisterRequest,
    WebhookRegisterResponse,
    WebhookListResponse,
    WebhookItem,
)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])

webhooks_db: dict[str, dict] = {}


VALID_EVENTS = [
    "document.uploaded",
    "document.analyzed",
    "document.deleted",
    "batch.completed",
    "analysis.completed",
]


@router.post("/register", response_model=WebhookRegisterResponse)
async def register_webhook(
    request: WebhookRegisterRequest,
    api_key: str = Depends(verify_api_key),
) -> WebhookRegisterResponse:
    """Register a new webhook."""
    for event in request.events:
        if event not in VALID_EVENTS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid event: {event}. Valid events: {VALID_EVENTS}",
            )

    webhook_id = str(uuid.uuid4())
    now = datetime.utcnow()

    webhook = {
        "id": webhook_id,
        "url": request.url,
        "events": request.events,
        "secret": request.secret,
        "enabled": request.enabled,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }

    webhooks_db[webhook_id] = webhook

    return WebhookRegisterResponse(
        id=webhook_id,
        url=request.url,
        events=request.events,
        enabled=request.enabled,
        created_at=now,
    )


@router.get("", response_model=WebhookListResponse)
async def list_webhooks(
    api_key: str = Depends(verify_api_key),
) -> WebhookListResponse:
    """List all registered webhooks."""
    webhooks = [
        WebhookItem(
            id=webhook["id"],
            url=webhook["url"],
            events=webhook["events"],
            enabled=webhook["enabled"],
            created_at=datetime.fromisoformat(webhook["created_at"]),
            updated_at=datetime.fromisoformat(webhook["updated_at"]),
        )
        for webhook in webhooks_db.values()
    ]

    return WebhookListResponse(
        total=len(webhooks),
        webhooks=webhooks,
    )


@router.delete("/{webhook_id}")
async def delete_webhook(
    webhook_id: str,
    api_key: str = Depends(verify_api_key),
) -> dict:
    """Delete a webhook."""
    if webhook_id not in webhooks_db:
        raise HTTPException(
            status_code=404,
            detail=f"Webhook not found: {webhook_id}",
        )

    del webhooks_db[webhook_id]

    return {
        "status": "deleted",
        "webhook_id": webhook_id,
    }