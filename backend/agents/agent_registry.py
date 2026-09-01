"""
Agent Capability Registry for Quorum.
Provides 8 general-purpose capabilities and dynamically instantiates between 4 and 8 agents
customized to the runtime CaseProfile and domain context without hard-coding specific test cases.
"""

from typing import List, Dict, Optional, Any
from crewai import Agent, LLM
from ..models.business_case import BusinessCase, CaseProfile
from ..case.domain_mapper import DomainMapper
from ..config import get_llm, is_verbose


class AgentRegistry:
    """Manages the 8 core capabilities and instantiates the active boardroom swarm."""

    def __init__(self, llm: Optional[LLM] = None, verbose: Optional[bool] = None):
        self.llm = llm or get_llm()
        self.verbose = verbose if verbose is not None else is_verbose()

    def assemble_board(self, business_case: BusinessCase, profile: Optional[CaseProfile] = None) -> List[Agent]:
        """
        Dynamically assembles the boardroom agents (strictly between 4 and 8 agents max)
        tailored to the active case.
        """
        active_capability_specs = DomainMapper.resolve_agent_capabilities(business_case)
        # Ensure hard ceiling of 8 active agents
        active_capability_specs = active_capability_specs[:8]

        agents: List[Agent] = []
        for cap_id, custom_title, domain_focus in active_capability_specs:
            agent = self.create_capability_agent(
                cap_id=cap_id,
                custom_title=custom_title,
                domain_focus=domain_focus,
                case=business_case,
                profile=profile
            )
            agents.append(agent)

        return agents

    def create_capability_agent(
        self,
        cap_id: str,
        custom_title: str,
        domain_focus: str,
        case: BusinessCase,
        profile: Optional[CaseProfile] = None
    ) -> Agent:
        """Instantiates an agent with customized domain instructions for its capability."""

        prompt_defs = {
            "business_research": {
                "role": custom_title,
                "goal": (
                    f"Analyze {case.title} from an evidence-based research perspective. Focus on: {domain_focus}. "
                    f"Distinguish strictly between FACT, CALCULATION, ASSUMPTION, and INFERENCE. "
                    f"Label missing data as 'NOT PROVIDED IN ACTIVE TEST CASE'. Never invent market statistics."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You analyze market signals, customer sentiment, "
                    f"and competitor moats based solely on the active case brief."
                )
            },
            "finance_economics": {
                "role": custom_title,
                "goal": (
                    f"Model financial feasibility, unit economics, CapEx/OpEx, margins, cash runway, and break-even timelines. "
                    f"Focus on: {domain_focus}. Calculate before recommending. "
                    f"Strictly enforce all hard budget and capital constraints."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You enforce fiscal discipline, calculate liquidity survival, "
                    f"and eliminate financially infeasible options."
                )
            },
            "risk": {
                "role": custom_title,
                "goal": (
                    f"Act as the adversarial stress-tester and reviewer. Focus on: {domain_focus}. "
                    f"Detect constraint breaches, solvency risks, operational bottlenecks, and cross-departmental contradictions. "
                    f"Challenge the leading proposal and construct the Strategy Comparison Matrix."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You never rubber-stamp proposals. Your mission is to "
                    f"protect enterprise survivability by exposing flawed assumptions and hidden risks."
                )
            },
            "product_strategy": {
                "role": custom_title,
                "goal": (
                    f"Formulate product architecture, feature roadmap, and strategic positioning. Focus on: {domain_focus}. "
                    f"Align product capabilities with real buyer needs and engineering capacity."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You bridge market demands with engineering execution."
                )
            },
            "operations_engineering": {
                "role": custom_title,
                "goal": (
                    f"Assess operational delivery, manufacturing/cloud throughput, lead times, and capacity constraints. "
                    f"Focus on: {domain_focus}. Quantify execution timelines and supply chain bottlenecks."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You evaluate whether candidate strategies can actually "
                    f"be delivered within hard capacity limits and regulatory lead times."
                )
            },
            "customer_marketing": {
                "role": custom_title,
                "goal": (
                    f"Develop commercial GTM, customer acquisition, distribution channels, and sales cycle models. "
                    f"Focus on: {domain_focus}. Quantify CAC, LTV, and conversion conversion economics without fabricating demand."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You drive revenue growth grounded in realistic customer discovery data."
                )
            },
            "compliance_quality": {
                "role": custom_title,
                "goal": (
                    f"Enforce regulatory compliance, customer protection standards, quality certifications, and audit readiness. "
                    f"Focus on: {domain_focus}. Enforce compliance as a non-negotiable hard constraint."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You ensure the company never violates consumer protection, "
                    f"security standards, or regulatory mandates."
                )
            },
            "ceo": {
                "role": custom_title,
                "goal": (
                    f"Synthesize specialist analyses, mathematical calculations, risk challenges, and the Strategy Comparison Matrix "
                    f"to make the definitive executive decision in the mandatory 13-section QUORUM Executive Decision format. "
                    f"Prioritize Compliance > Hard Constraints > Liquidity > Feasibility > Value."
                ),
                "backstory": (
                    f"You are the {custom_title} in QUORUM. You lead the boardroom, resolve debate, enforce operational reality, "
                    f"and deliver high-conviction, evidence-based executive mandates."
                )
            }
        }

        spec = prompt_defs.get(cap_id, prompt_defs["operations_engineering"])
        return Agent(
            role=spec["role"],
            goal=spec["goal"],
            backstory=spec["backstory"],
            llm=self.llm,
            verbose=self.verbose,
            allow_delegation=False,
        )
