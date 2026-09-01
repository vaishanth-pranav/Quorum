"""
Definitions of the Boardroom Specialist Agents for Quorum using CrewAI.
Supports both classic fixed 6-agent accessors (for backward compatibility with tests)
and dynamic capability-based assembly via AgentRegistry (strictly <= 8 agents).
"""

from typing import Optional, List
from crewai import Agent, LLM
from .agent_registry import AgentRegistry
from ..models.business_case import BusinessCase, CaseProfile, DUMMY_BUSINESS_CASE
from ..config import get_llm, is_verbose


class BoardAgents:
    """Manages boardroom agent creation with backward-compatible method names."""

    def __init__(self, llm: Optional[LLM] = None, business_case: Optional[BusinessCase] = None):
        self.llm = llm or get_llm()
        self.verbose = is_verbose()
        self.business_case = business_case or DUMMY_BUSINESS_CASE
        self.registry = AgentRegistry(llm=self.llm, verbose=self.verbose)

    def assemble_board(self, case: Optional[BusinessCase] = None, profile: Optional[CaseProfile] = None) -> List[Agent]:
        """Dynamically assemble between 4 and 8 agents for the case."""
        target_case = case or self.business_case
        return self.registry.assemble_board(business_case=target_case, profile=profile)

    def business_research_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="business_research",
            custom_title="Chief Market & Business Intelligence Analyst",
            domain_focus="Market dynamics, customer demand signals, competitor positioning",
            case=self.business_case
        )

    def finance_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="finance_economics",
            custom_title="Chief Financial Officer (CFO)",
            domain_focus="Financial modeling, unit economics, CapEx/OpEx, liquidity runway, and budget caps",
            case=self.business_case
        )

    def marketing_sales_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="customer_marketing",
            custom_title="Chief Marketing & Commercial Officer (CMO)",
            domain_focus="Go-to-market strategy, customer acquisition cost (CAC), LTV, and conversion funnels",
            case=self.business_case
        )

    def operations_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="operations_engineering",
            custom_title="Head of Global Operations & Infrastructure",
            domain_focus="Operational feasibility, execution lead times, capacity limits, supply chain",
            case=self.business_case
        )

    def risk_reviewer_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="risk",
            custom_title="Chief Risk Officer & Boardroom Reviewer (CRO)",
            domain_focus="Adversarial challenge, flaw identification, solvency stress-testing, and strategy matrix",
            case=self.business_case
        )

    def product_strategy_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="product_strategy",
            custom_title="Chief Product & Strategy Officer (CPSO)",
            domain_focus="Product architecture, roadmap prioritization, and feature packaging",
            case=self.business_case
        )

    def compliance_quality_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="compliance_quality",
            custom_title="Chief Compliance & Quality Officer (CCQO)",
            domain_focus="Regulatory compliance, customer protection, security audits, and reliability",
            case=self.business_case
        )

    def ceo_agent(self) -> Agent:
        return self.registry.create_capability_agent(
            cap_id="ceo",
            custom_title="Chief Executive Officer (CEO)",
            domain_focus="Strategic synthesis, constraint reconciliation, and 13-section Executive Decision",
            case=self.business_case
        )


def create_board_agents(llm: Optional[LLM] = None, business_case: Optional[BusinessCase] = None) -> BoardAgents:
    return BoardAgents(llm=llm, business_case=business_case)
