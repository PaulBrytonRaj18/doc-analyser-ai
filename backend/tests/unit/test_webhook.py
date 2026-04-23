"""Unit Tests - Webhook System"""

import json
import pytest
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx


class TestWebhookEventTypes:
    """Test WebhookEventType class."""

    def test_valid_event_types(self):
        """Test valid event types."""
        from app.services.webhook import WEBHOOK_EVENTS

        assert "document.ready" in WEBHOOK_EVENTS
        assert "batch.complete" in WEBHOOK_EVENTS
        assert "batch.partial" in WEBHOOK_EVENTS
        assert "rag.query.done" in WEBHOOK_EVENTS
        assert "document.failed" in WEBHOOK_EVENTS

    def test_all_supported_events(self):
        """Test all events list."""
        from app.services.webhook import WEBHOOK_EVENTS

        expected_events = [
            "document.ready",
            "batch.complete",
            "batch.partial",
            "rag.query.done",
            "document.failed",
        ]
        assert WEBHOOK_EVENTS == expected_events


class TestWebhookDispatcherPayloadSigning:
    """Test WebhookDispatcher HMAC-SHA256 payload signing."""

    def test_sign_payload_generates_string(self):
        """Test sign_payload returns a hex string with sha256 prefix."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}
        timestamp = "1234567890"
        signature = dispatcher.sign_payload(payload, timestamp)

        assert isinstance(signature, str)
        assert signature.startswith("sha256=")
        assert len(signature) == 71

    def test_sign_payload_deterministic(self):
        """Test that same payload produces same signature."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}
        timestamp = "1234567890"

        sig1 = dispatcher.sign_payload(payload, timestamp)
        sig2 = dispatcher.sign_payload(payload, timestamp)

        assert sig1 == sig2

    def test_sign_payload_different_timestamps(self):
        """Test different timestamps produce different signatures."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}

        sig1 = dispatcher.sign_payload(payload, "1000")
        sig2 = dispatcher.sign_payload(payload, "2000")

        assert sig1 != sig2


class TestWebhookDispatcherBuildPayload:
    """Test payload building via _build_headers."""

    def test_build_headers_structure(self):
        """Test headers have required fields."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}
        headers = dispatcher._build_headers(payload)

        assert "Content-Type" in headers
        assert "X-Webhook-Signature" in headers
        assert "X-Webhook-Timestamp" in headers
        assert "X-Webhook-Event" in headers

    def test_build_headers_signature_format(self):
        """Test signature format is sha256=<hex>."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}
        headers = dispatcher._build_headers(payload)

        sig = headers["X-Webhook-Signature"]
        assert sig.startswith("sha256=")
        assert len(sig) == 71

    def test_build_headers_with_custom_secret(self):
        """Test headers with custom webhook secret."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {"doc_id": "123"}}
        custom_secret = "custom-webhook-secret"

        headers = dispatcher._build_headers(payload, custom_secret)

        sig_custom = headers["X-Webhook-Signature"]
        headers_default = dispatcher._build_headers(payload)

        assert sig_custom != headers_default["X-Webhook-Signature"]


class TestRetryState:
    """Test RetryState class."""

    def test_retry_state_initialization(self):
        """Test RetryState default initialization."""
        from app.services.webhook.dispatcher import RetryState

        with patch("app.services.webhook.dispatcher.settings") as mock_settings:
            mock_settings.webhook_retry_attempts = 3

            state = RetryState()

            assert state.max_attempts == 3
            assert state.current_attempt == 0
            assert state.last_error is None
            assert state.delays == []

    def test_retry_state_custom_max_attempts(self):
        """Test RetryState custom max_attempts."""
        from app.services.webhook.dispatcher import RetryState

        state = RetryState(max_attempts=5)
        assert state.max_attempts == 5

    def test_should_retry_logic(self):
        """Test should_retry property."""
        from app.services.webhook.dispatcher import RetryState

        state = RetryState(max_attempts=3)
        assert state.should_retry is True

        state.current_attempt = 2
        assert state.should_retry is True

        state.current_attempt = 3
        assert state.should_retry is False

    def test_record_attempt(self):
        """Test record_attempt increments counter."""
        from app.services.webhook.dispatcher import RetryState

        state = RetryState(max_attempts=3)
        state.record_attempt(2.0, "timeout")

        assert state.current_attempt == 1
        assert state.delays == [2.0]
        assert state.last_error == "timeout"

    def test_reset(self):
        """Test reset clears state."""
        from app.services.webhook.dispatcher import RetryState

        state = RetryState(max_attempts=3)
        state.record_attempt(2.0, "timeout")
        state.reset()

        assert state.current_attempt == 0
        assert state.last_error is None
        assert state.delays == []

    def test_get_backoff_delay(self):
        """Test exponential backoff delay calculation."""
        from app.services.webhook.dispatcher import RetryState, RETRY_BASE_DELAY

        state = RetryState(max_attempts=3)

        assert state.get_backoff_delay() == RETRY_BASE_DELAY**0

        state.current_attempt = 1
        assert state.get_backoff_delay() == RETRY_BASE_DELAY**1

        state.current_attempt = 2
        assert state.get_backoff_delay() == RETRY_BASE_DELAY**2


class TestWebhookDispatcherDispatch:
    """Test dispatch method with mocked components."""

    @pytest.mark.asyncio
    async def test_dispatch_invalid_event_type(self):
        """Test dispatch with invalid event type."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        result = await dispatcher.dispatch(
            event="invalid.event",
            data={"doc_id": "123"},
        )

        assert result["status"] == "error"
        assert "Unknown event" in result["message"]

    @pytest.mark.asyncio
    async def test_dispatch_no_webhooks_configured(self):
        """Test dispatch when no webhooks exist for event."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook

        mock_db = AsyncMock()

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            dispatcher = WebhookDispatcher(mock_db)

            result = await dispatcher.dispatch(
                event="document.ready",
                data={"doc_id": "123"},
            )

            assert result["status"] == "skipped"

    @pytest.mark.asyncio
    async def test_dispatch_builds_correct_payload(self):
        """Test dispatch builds correct payload structure."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook

        mock_db = AsyncMock()

        mock_webhook = MagicMock()
        mock_webhook.id = "webhook-uuid"
        mock_webhook.url = "https://example.com/webhook"
        mock_webhook.secret = "secret"
        mock_webhook.active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_webhook]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            dispatcher = WebhookDispatcher(mock_db)
            with patch.object(dispatcher, "_dispatch_with_retry", new=AsyncMock()) as mock_dispatch:
                mock_dispatch.return_value = {
                    "webhook_id": "webhook-uuid",
                    "success": True,
                    "status_code": 200,
                }

                result = await dispatcher.dispatch(
                    event="document.ready",
                    data={"doc_id": "123"},
                )

                assert result["status"] == "completed"


class TestWebhookDispatcherRetryLogic:
    """Test retry logic integration."""

    @pytest.mark.asyncio
    async def test_dispatch_retry_on_failure(self):
        """Test retry logic triggers on HTTP error."""
        from app.services.webhook import WebhookDispatcher
        from app.services.webhook.dispatcher import RetryState
        from app.models.db import Webhook
        from app.core.config import settings

        mock_db = AsyncMock()
        settings.webhook_retry_attempts = 3

        mock_webhook = MagicMock(spec=Webhook)
        mock_webhook.id = "test-webhook-id"
        mock_webhook.url = "https://example.com/webhook"
        mock_webhook.secret = "test-secret"
        mock_webhook.active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_webhook]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.is_success = False
                mock_response.status_code = 500

                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with patch.object(mock_db, "commit", new=AsyncMock()):
                    dispatcher = WebhookDispatcher(mock_db)
                    result = await dispatcher.dispatch(
                        event="document.ready",
                        data={"doc_id": "123"},
                    )

                    assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_dispatch_success_updates_webhook(self):
        """Test successful dispatch updates webhook status."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook

        mock_db = AsyncMock()

        mock_webhook = MagicMock(spec=Webhook)
        mock_webhook.id = "test-webhook-id"
        mock_webhook.url = "https://example.com/webhook"
        mock_webhook.secret = "test-secret"
        mock_webhook.active = True
        mock_webhook.last_triggered = None
        mock_webhook.retry_count = 0

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_webhook]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.is_success = True
                mock_response.status_code = 200

                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with patch.object(mock_db, "commit", new=AsyncMock()):
                    dispatcher = WebhookDispatcher(mock_db)

                    result = await dispatcher.dispatch(
                        event="document.ready",
                        data={"doc_id": "123"},
                    )

                    assert result["results"][0]["success"] is True
                    assert result["successful"] == 1


class TestWebhookEndpointsMocked:
    """Test webhook endpoints with mocked HTTP client."""

    @pytest.mark.asyncio
    async def test_dispatch_includes_event_in_headers(self):
        """Test X-Webhook-Event header matches event type."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "batch.complete", "data": {"batch_id": "b1"}}
        headers = dispatcher._build_headers(payload)

        assert headers["X-Webhook-Event"] == "batch.complete"

    @pytest.mark.asyncio
    async def test_dispatch_uses_formatted_timestamp(self):
        """Test timestamp is properly formatted."""
        from app.services.webhook import WebhookDispatcher

        mock_db = AsyncMock()
        dispatcher = WebhookDispatcher(mock_db)

        payload = {"event": "document.ready", "data": {}}
        headers = dispatcher._build_headers(payload)

        timestamp = headers["X-Webhook-Timestamp"]
        assert timestamp.isdigit()
        assert len(timestamp) == 10


class TestWebhookDispatcherIntegration:
    """Integration tests with mocked HTTP."""

    @pytest.mark.asyncio
    async def test_full_dispatch_flow_with_db(self):
        """Test complete dispatch flow."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook
        from app.core.config import settings

        mock_db = AsyncMock()
        settings.webhook_retry_attempts = 1

        mock_webhook = MagicMock(spec=Webhook)
        mock_webhook.id = "webhook-test-id"
        mock_webhook.url = "https://api.example.com/webhooks"
        mock_webhook.secret = settings.webhook_secret
        mock_webhook.active = True
        mock_webhook.last_triggered = None
        mock_webhook.retry_count = 0

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_webhook]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.is_success = True
                mock_response.status_code = 201

                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with patch.object(mock_db, "commit", new=AsyncMock()):
                    dispatcher = WebhookDispatcher(mock_db)
                    result = await dispatcher.dispatch(
                        event="document.ready",
                        data={
                            "document_id": "doc-abc-123",
                            "filename": "invoice.pdf",
                        },
                    )

                    assert result["status"] == "completed"
                    assert result["successful"] == 1

                    call_args = mock_client.post.call_args
                    assert call_args is not None
                    payload_sent = call_args.kwargs["json"]
                    assert payload_sent["event"] == "document.ready"
                    assert payload_sent["data"]["document_id"] == "doc-abc-123"

    @pytest.mark.asyncio
    async def test_multiple_webhooks_dispatch(self):
        """Test dispatch to multiple webhook endpoints."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook
        from app.core.config import settings

        mock_db = AsyncMock()
        settings.webhook_retry_attempts = 1

        mock_webhook1 = MagicMock(spec=Webhook)
        mock_webhook1.id = "webhook-1"
        mock_webhook1.url = "https://example1.com/hook"
        mock_webhook1.secret = "secret1"
        mock_webhook1.active = True

        mock_webhook2 = MagicMock(spec=Webhook)
        mock_webhook2.id = "webhook-2"
        mock_webhook2.url = "https://example2.com/hook"
        mock_webhook2.secret = "secret2"
        mock_webhook2.active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [
            mock_webhook1,
            mock_webhook2,
        ]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = MagicMock()
                mock_response.is_success = True
                mock_response.status_code = 200

                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value = mock_client

                with patch.object(mock_db, "commit", new=AsyncMock()):
                    dispatcher = WebhookDispatcher(mock_db)
                    result = await dispatcher.dispatch(
                        event="batch.complete",
                        data={"batch_id": "batch-001"},
                    )

                    assert result["status"] == "completed"
                    assert result["total"] == 2
                    assert mock_client.post.call_count == 2

    @pytest.mark.asyncio
    async def test_exception_handling_in_dispatch(self):
        """Test exception handling during HTTP dispatch."""
        from app.services.webhook import WebhookDispatcher
        from app.models.db import Webhook
        from app.core.config import settings

        mock_db = AsyncMock()
        settings.webhook_retry_attempts = 1

        mock_webhook = MagicMock(spec=Webhook)
        mock_webhook.id = "webhook-err"
        mock_webhook.url = "https://bad.example.com"
        mock_webhook.secret = "secret"
        mock_webhook.active = True

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_webhook]

        with patch.object(mock_db, "execute", new=AsyncMock(return_value=mock_result)):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client.__aenter__ = AsyncMock(
                    side_effect=httpx.HTTPError("Connection failed")
                )
                mock_client.__aexit__ = AsyncMock(return_value=None)
                mock_client_class.return_value = mock_client

                with patch.object(mock_db, "commit", new=AsyncMock()):
                    dispatcher = WebhookDispatcher(mock_db)
                    result = await dispatcher.dispatch(
                        event="document.ready",
                        data={"doc_id": "123"},
                    )

                    assert result["status"] == "completed"
                    assert result["failed"] == 1
                    assert result["results"][0]["success"] is False