"""
ATLAS Workflow Tests
"""

import pytest
from unittest.mock import MagicMock, patch
from orchestration.coordination import AgentCoordinator, EVENTS


class TestAgentCoordinator:
    """Test Redis coordination layer."""

    def test_events_dict_has_all_keys(self):
        required = [
            'LEAD_RECEIVED', 'LEAD_ENRICHED', 'LEAD_QUALIFIED',
            'OUTREACH_SENT', 'REPLY_RECEIVED', 'APPOINTMENT_BOOKED',
            'PAYMENT_RECEIVED', 'LEAD_OPTED_OUT',
        ]
        for key in required:
            assert key in EVENTS, f"Missing event: {key}"

    def test_coordinator_instantiates(self):
        with patch('orchestration.coordination.redis') as mock_redis:
            mock_redis.from_url.return_value = MagicMock()
            coordinator = AgentCoordinator()
            assert coordinator is not None

    def test_suppress_lead_calls_redis(self):
        with patch('orchestration.coordination.redis') as mock_redis:
            mock_client = MagicMock()
            mock_redis.from_url.return_value = mock_client
            coordinator = AgentCoordinator()
            coordinator.client = mock_client
            coordinator.suppress_lead('+12145550123')
            mock_client.sadd.assert_called_once_with(
                'atlas:suppressed_phones', '+12145550123'
            )


class TestLeadStateSchema:
    """Test state schema completeness."""

    def test_state_has_compliance_fields(self):
        from orchestration.state import LeadState
        annotations = LeadState.__annotations__
        compliance_fields = ['consent_verified', 'consent_timestamp', 'suppressed']
        for field in compliance_fields:
            assert field in annotations, f"Missing compliance field: {field}"

    def test_state_has_pipeline_flags(self):
        from orchestration.state import LeadState
        annotations = LeadState.__annotations__
        pipeline_fields = ['outreach_sent', 'appointment_booked', 'quote_sent', 'payment_received']
        for field in pipeline_fields:
            assert field in annotations, f"Missing pipeline field: {field}"
