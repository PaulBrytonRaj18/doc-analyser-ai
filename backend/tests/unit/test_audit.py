"""Unit Tests - Audit Logging"""

from unittest.mock import MagicMock


class TestAuditLogger:
    """Test Audit logging functionality."""

    def test_compute_hash(self):
        """Test SHA-256 hash computation."""
        from app.core.audit import AuditLogger

        logger = AuditLogger(db=MagicMock())

        data = {
            "timestamp": "2024-01-01T00:00:00",
            "request_id": "test_001",
            "action": "UPLOAD",
            "request_path": "/v1/upload",
            "request_method": "POST",
            "response_status": 200,
            "previous_hash": None,
        }

        hash_result = logger._compute_hash(data, None)

        # Verify hash is SHA-256 hex string
        assert len(hash_result) == 64
        assert all(c in "0123456789abcdef" for c in hash_result)

    def test_compute_hash_with_previous(self):
        """Test hash with previous hash in chain."""
        from app.core.audit import AuditLogger

        logger = AuditLogger(db=MagicMock())

        data = {
            "timestamp": "2024-01-02T00:00:00",
            "request_id": "test_002",
            "action": "QUERY",
            "request_path": "/v1/rag/query",
            "request_method": "POST",
            "response_status": 200,
            "previous_hash": "abc123",
        }

        hash_result = logger._compute_hash(data, "abc123")

        assert len(hash_result) == 64

    def test_audit_data_structure(self):
        """Test audit data structure for hashing."""
        from app.core.audit import AuditLogger

        logger = AuditLogger(db=MagicMock())

        data = {
            "timestamp": "2024-01-01T12:00:00",
            "request_id": "req_001",
            "user_id": "user_001",
            "action": "DELETE",
            "resource_type": "document",
            "resource_id": "doc_001",
            "request_path": "/v1/documents/doc_001",
            "request_method": "DELETE",
            "response_status": 204,
            "ip_address": "192.168.1.1",
            "user_agent": "Mozilla/5.0",
            "previous_hash": "prev_hash_abc",
        }

        required_fields = [
            "timestamp",
            "request_id",
            "user_id",
            "action",
            "resource_type",
            "resource_id",
            "request_path",
            "request_method",
            "response_status",
            "ip_address",
            "user_agent",
            "previous_hash",
        ]

        for field in required_fields:
            assert field in data, f"Missing field: {field}"

        # Hash should be deterministic
        hash1 = logger._compute_hash(data, data["previous_hash"])
        hash2 = logger._compute_hash(data, data["previous_hash"])
        assert hash1 == hash2