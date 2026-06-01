"""
ATLAS Master Orchestration Workflow
LangGraph state machine — routes leads through all 7 agents.
"""
from typing import TypedDict, Literal
from enum import Enum


class LeadState(str, Enum):
    NEW = "new"
    ENRICHED = "enriched"
    QUALIFIED = "qualified"
    OUTREACH_SENT = "outreach_sent"
    IN_CONVERSATION = "in_conversation"
    BOOKED = "booked"
    QUOTE_SENT = "quote_sent"
    PAID = "paid"
    REJECTED = "rejected"
    OPTED_OUT = "opted_out"


class ATLASState(TypedDict):
    lead_id: str
    name: str
    phone: str
    address: str
    score: float
    tier: str
    state: str
    messages: list[dict]
    next_action: str


def route_lead(state: ATLASState) -> Literal[
    "enrich", "qualify", "outreach", "converse", "schedule", "invoice", "end"
]:
    """State router — decides next agent based on current lead state."""
    s = state.get("state", "new")
    routes = {
        "new": "enrich",
        "enriched": "qualify",
        "qualified": "outreach",
        "outreach_sent": "converse",
        "in_conversation": "schedule",
        "booked": "invoice",
        "paid": "end",
        "rejected": "end",
        "opted_out": "end",
    }
    return routes.get(s, "end")
