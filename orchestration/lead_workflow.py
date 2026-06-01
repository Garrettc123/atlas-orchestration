"""
ATLAS Lead Workflow
LangGraph state machine orchestrating all 7 agents.
"""

from langgraph.graph import StateGraph, END
from .state import LeadState
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ATLASWorkflow:
    """Full lead pipeline state machine."""

    def __init__(self):
        self.workflow = StateGraph(LeadState)
        self._build_graph()

    def _build_graph(self):
        """Wire all nodes and edges."""

        # Register nodes
        nodes = [
            ('prospect', self.prospect),
            ('qualify', self.qualify),
            ('outreach', self.outreach),
            ('converse', self.converse),
            ('schedule', self.schedule),
            ('revenue', self.revenue),
            ('analyze', self.analyze),
        ]
        for name, fn in nodes:
            self.workflow.add_node(name, fn)

        # Entry
        self.workflow.set_entry_point('prospect')

        # Linear edges
        self.workflow.add_edge('prospect', 'qualify')

        # Conditional routing by score
        self.workflow.add_conditional_edges(
            'qualify',
            self._route_by_score,
            {'hot': 'outreach', 'warm': 'outreach', 'cold': 'analyze'},
        )

        # Outreach -> converse
        self.workflow.add_edge('outreach', 'converse')

        # Conditional routing by engagement
        self.workflow.add_conditional_edges(
            'converse',
            self._route_by_engagement,
            {
                'ready': 'schedule',
                'objection': 'converse',
                'unresponsive': 'analyze',
            },
        )

        self.workflow.add_edge('schedule', 'revenue')
        self.workflow.add_edge('revenue', 'analyze')
        self.workflow.add_edge('analyze', END)

    # ──────────────────────────────────
    # Agent Nodes
    # ──────────────────────────────────

    def prospect(self, state: LeadState) -> LeadState:
        from atlas_agents import ProspectorAgent
        enriched = ProspectorAgent().enrich_lead(state['raw_data'])
        state['enriched_data'] = enriched
        state['current_stage'] = 'prospected'
        state['timestamps']['prospected_at'] = datetime.utcnow().isoformat()
        logger.info(f"[{state['lead_id']}] Prospecting complete")
        return state

    def qualify(self, state: LeadState) -> LeadState:
        from atlas_agents import QualifierAgent
        scored = QualifierAgent().score_lead(state['enriched_data'])
        state['score'] = scored.get('score', 0)
        state['tier'] = scored.get('tier', 'cold')
        state['priority'] = scored.get('priority', 5)
        state['current_stage'] = 'qualified'
        state['timestamps']['qualified_at'] = datetime.utcnow().isoformat()
        logger.info(f"[{state['lead_id']}] Score: {state['score']} Tier: {state['tier']}")
        return state

    def outreach(self, state: LeadState) -> LeadState:
        from atlas_agents import OutreachAgent
        channel = 'sms' if state['tier'] == 'hot' else 'email'
        msg = OutreachAgent().generate_outreach(state['enriched_data'], channel)
        state['outreach_sent'] = msg.get('compliant', False)
        state['outreach_channel'] = channel
        state['current_stage'] = 'outreach_sent'
        state['timestamps']['outreach_at'] = datetime.utcnow().isoformat()
        logger.info(f"[{state['lead_id']}] Outreach sent via {channel}")
        return state

    def converse(self, state: LeadState) -> LeadState:
        # Placeholder: Conversation agent handles inbound replies
        state['current_stage'] = 'in_conversation'
        return state

    def schedule(self, state: LeadState) -> LeadState:
        # Placeholder: Scheduler agent books calendar slot
        state['appointment_booked'] = True
        state['current_stage'] = 'appointment_booked'
        state['timestamps']['booked_at'] = datetime.utcnow().isoformat()
        logger.info(f"[{state['lead_id']}] Appointment booked")
        return state

    def revenue(self, state: LeadState) -> LeadState:
        # Placeholder: Revenue agent generates quote + Stripe link
        state['quote_sent'] = True
        state['current_stage'] = 'quote_sent'
        logger.info(f"[{state['lead_id']}] Quote sent")
        return state

    def analyze(self, state: LeadState) -> LeadState:
        state['current_stage'] = 'complete'
        state['timestamps']['completed_at'] = datetime.utcnow().isoformat()
        logger.info(f"[{state['lead_id']}] Pipeline complete")
        return state

    # ──────────────────────────────────
    # Routing Logic
    # ──────────────────────────────────

    def _route_by_score(self, state: LeadState) -> str:
        return state.get('tier', 'cold')

    def _route_by_engagement(self, state: LeadState) -> str:
        if state.get('appointment_booked'):
            return 'ready'
        if len(state.get('conversation_history', [])) > 5:
            return 'objection'
        return 'unresponsive'

    def run(self, raw_lead: dict, client_id: str = 'default') -> dict:
        """Execute full pipeline for a single lead."""
        app = self.workflow.compile()

        initial: LeadState = {
            'lead_id': raw_lead.get('id', 'unknown'),
            'client_id': client_id,
            'raw_data': raw_lead,
            'enriched_data': {},
            'score': 0,
            'tier': 'cold',
            'priority': 5,
            'consent_verified': False,
            'consent_timestamp': None,
            'suppressed': False,
            'outreach_sent': False,
            'outreach_channel': '',
            'appointment_booked': False,
            'quote_sent': False,
            'payment_received': False,
            'conversation_history': [],
            'engagement_score': 0,
            'current_stage': 'initiated',
            'errors': [],
            'timestamps': {'initiated_at': datetime.utcnow().isoformat()},
        }

        return app.invoke(initial)
