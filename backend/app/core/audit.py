"""
Audit Logging - DocuLens AI v4.0
Tamper-Evident SHA-256 Chain
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.db import AuditLog


class AuditLogger:
    """Tamper-evident audit logger with SHA-256 chain."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_last_hash(self) -> Optional[str]:
        """Get the hash of the most recent audit log entry."""
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(1)
        )
        last_entry = result.scalar_one_or_none()
        return last_entry.current_hash if last_entry else None

    def _compute_hash(
        self, data: dict, previous_hash: Optional[str] = None
    ) -> str:
        """Compute SHA-256 hash for audit entry."""
        hash_input = json.dumps(data, sort_keys=True, default=str)
        if previous_hash:
            hash_input += previous_hash
        return hashlib.sha256(hash_input.encode()).hexdigest()

    async def log(
        self,
        action: str,
        request_path: str,
        request_method: str,
        response_status: int,
        request_id: Optional[str] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[dict] = None,
    ) -> AuditLog:
        """Create a tamper-evident audit log entry."""
        if not settings.audit_log_enabled:
            return None

        request_id = request_id or str(uuid.uuid4())
        previous_hash = await self._get_last_hash()
        timestamp = datetime.utcnow()

        data = {
            "timestamp": timestamp.isoformat(),
            "request_id": request_id,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "request_path": request_path,
            "request_method": request_method,
            "response_status": response_status,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "previous_hash": previous_hash,
        }

        current_hash = self._compute_hash(data, previous_hash)

        audit_entry = AuditLog(
            timestamp=timestamp,
            request_id=request_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_path=request_path,
            request_method=request_method,
            response_status=response_status,
            ip_address=ip_address,
            user_agent=user_agent,
            previous_hash=previous_hash,
            current_hash=current_hash,
            extra_data=extra_data,
        )

        self.db.add(audit_entry)
        await self.db.commit()
        return audit_entry

    async def verify_chain(self) -> tuple[bool, list[dict]]:
        """Verify the integrity of the audit chain."""
        result = await self.db.execute(
            select(AuditLog).order_by(AuditLog.timestamp.asc())
        )
        entries = result.scalars().all()

        if not entries:
            return True, []

        validation_errors = []
        for i, entry in enumerate(entries):
            computed_hash = self._compute_hash(
                {
                    "timestamp": entry.timestamp.isoformat(),
                    "request_id": entry.request_id,
                    "user_id": entry.user_id,
                    "action": entry.action,
                    "resource_type": entry.resource_type,
                    "resource_id": entry.resource_id,
                    "request_path": entry.request_path,
                    "request_method": entry.request_method,
                    "response_status": entry.response_status,
                    "ip_address": entry.ip_address,
                    "user_agent": entry.user_agent,
                    "previous_hash": entry.previous_hash,
                },
                entry.previous_hash,
            )

            if computed_hash != entry.current_hash:
                validation_errors.append(
                    {
                        "entry_id": str(entry.id),
                        "request_id": entry.request_id,
                        "expected_hash": entry.current_hash,
                        "computed_hash": computed_hash,
                    }
                )

        return len(validation_errors) == 0, validation_errors

    async def get_logs(
        self,
        limit: int = 100,
        offset: int = 0,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
    ) -> list[AuditLog]:
        """Retrieve audit logs with filters."""
        query = select(AuditLog).order_by(AuditLog.timestamp.desc())

        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if action:
            query = query.where(AuditLog.action == action)

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars().all())


async def get_audit_logger(db: AsyncSession) -> AuditLogger:
    """Factory function to get audit logger instance."""
    return AuditLogger(db)