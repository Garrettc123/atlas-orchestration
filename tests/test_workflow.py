"""Orchestration routing tests."""
from orchestration.workflow import route_lead


def test_new_lead_routes_to_enrich():
    state = {"lead_id": "1", "state": "new", "score": 0, "messages": []}
    assert route_lead(state) == "enrich"


def test_qualified_routes_to_outreach():
    state = {"lead_id": "1", "state": "qualified", "score": 75, "messages": []}
    assert route_lead(state) == "outreach"


def test_paid_routes_to_end():
    state = {"lead_id": "1", "state": "paid", "score": 95, "messages": []}
    assert route_lead(state) == "end"


def test_opted_out_routes_to_end():
    state = {"lead_id": "1", "state": "opted_out", "score": 40, "messages": []}
    assert route_lead(state) == "end"
