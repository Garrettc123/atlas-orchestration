"""
ATLAS Agent Coordination
Redis pub/sub event bus for inter-agent communication.
"""

import redis
import json
import os
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)

EVENTS = {
    'LEAD_RECEIVED': 'lead_received',
    'LEAD_ENRICHED': 'lead_enriched',
    'LEAD_QUALIFIED': 'lead_qualified',
    'OUTREACH_SENT': 'outreach_sent',
    'REPLY_RECEIVED': 'reply_received',
    'APPOINTMENT_BOOKED': 'appointment_booked',
    'PAYMENT_RECEIVED': 'payment_received',
    'LEAD_OPTED_OUT': 'lead_opted_out',
}


class AgentCoordinator:
    """Redis pub/sub event bus — decouples agents from direct calls."""

    def __init__(self):
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.client = redis.from_url(redis_url, decode_responses=True)
        self.pubsub = self.client.pubsub()
        self.handlers: Dict[str, Callable] = {}

    def publish(self, event_type: str, data: dict):
        """Publish event to Redis channel."""
        payload = json.dumps({'event': event_type, 'data': data})
        channel = f'atlas:{event_type}'
        self.client.publish(channel, payload)
        logger.info(f"Event published: {event_type}")

    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to an event type with a handler function."""
        self.pubsub.subscribe(f'atlas:{event_type}')
        self.handlers[event_type] = handler

    def listen(self):
        """Block and process incoming events."""
        for msg in self.pubsub.listen():
            if msg['type'] == 'message':
                payload = json.loads(msg['data'])
                event = payload.get('event')
                if event in self.handlers:
                    self.handlers[event](payload.get('data'))

    def cache_state(self, lead_id: str, state: dict, ttl: int = 3600):
        self.client.setex(f'lead:{lead_id}:state', ttl, json.dumps(state))

    def get_state(self, lead_id: str) -> dict:
        raw = self.client.get(f'lead:{lead_id}:state')
        return json.loads(raw) if raw else {}

    def suppress_lead(self, phone: str):
        """Add phone to suppression list (TCPA opt-out)."""
        self.client.sadd('atlas:suppressed_phones', phone)
        logger.info(f"Phone suppressed: {phone[-4:]}****")

    def is_suppressed(self, phone: str) -> bool:
        return self.client.sismember('atlas:suppressed_phones', phone)
