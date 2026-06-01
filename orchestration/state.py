"""
ATLAS Lead State Schema
Shared state object passed between all agents in the workflow.
"""

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
import operator


class LeadState(TypedDict):
    """Immutable state object passed between agents."""

    # Identity
    lead_id: str
    client_id: str

    # Raw & enriched data
    raw_data: dict
    enriched_data: dict

    # Qualification
    score: int
    tier: str  # hot | warm | cold
    priority: int  # 1-5

    # Compliance
    consent_verified: bool
    consent_timestamp: Optional[str]
    suppressed: bool

    # Pipeline stage flags
    outreach_sent: bool
    outreach_channel: str  # sms | email
    appointment_booked: bool
    quote_sent: bool
    payment_received: bool

    # Conversation
    conversation_history: Annotated[Sequence[BaseMessage], operator.add]
    engagement_score: int  # 0-10

    # Meta
    current_stage: str
    errors: list
    timestamps: dict
