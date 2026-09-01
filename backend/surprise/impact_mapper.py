"""
Surprise Impact Mapping Layer for Quorum.
Compares injected surprise events against the active CaseProfile, classifies previous findings
into VALID / PARTIALLY AFFECTED / INVALIDATED, and determines the targeted subset of agents to rerun.
"""

from typing import List, Dict, Set, Any
from ..models.business_case import BusinessCase, CaseProfile, SurpriseEvent


class ImpactMapper:
    """Performs impact analysis to prevent unnecessary total swarm restarts."""

    @classmethod
    def analyze_impact(
        cls,
        surprise: SurpriseEvent,
        case: BusinessCase,
        profile: CaseProfile
    ) -> Dict[str, Any]:
        """
        Calculates impact dimensions from the surprise event.
        """
        desc_lower = surprise.description.lower()
        invalidated: List[str] = list(surprise.changed_assumptions)
        affected_agents: Set[str] = set()

        # Add explicit affected departments with normalized capability names
        for dept in surprise.affected_departments:
            dept_lower = dept.lower()
            if "compliance" in dept_lower or "protection" in dept_lower or "quality" in dept_lower:
                affected_agents.add("Compliance / Quality")
            elif "finance" in dept_lower or "treasury" in dept_lower or "cfo" in dept_lower or "economics" in dept_lower:
                affected_agents.add("Finance & Economics")
            elif "customer" in dept_lower or "marketing" in dept_lower or "sales" in dept_lower or "cmo" in dept_lower:
                affected_agents.add("Customer / Marketing")
            elif "operation" in dept_lower or "engineering" in dept_lower or "manufacturing" in dept_lower or "supply" in dept_lower:
                affected_agents.add("Operations / Engineering")
            elif "risk" in dept_lower or "cro" in dept_lower:
                affected_agents.add("Risk")
            elif "product" in dept_lower or "strategy" in dept_lower:
                affected_agents.add("Product / Strategy")
            elif "research" in dept_lower or "intelligence" in dept_lower:
                affected_agents.add("Business Research")
            else:
                affected_agents.add(dept)


        # Infer additional affected domains from description keywords
        if any(w in desc_lower for w in ["budget", "capital", "cost", "burn", "price", "cogs", "loss", "default"]):
            affected_agents.add("Finance & Economics")
        if any(w in desc_lower for w in ["tool", "fab", "outage", "supply", "lead time", "delay", "wafer", "hardware"]):
            affected_agents.add("Operations / Engineering")
        if any(w in desc_lower for w in ["competitor", "churn", "demand", "customer", "sales", "merchant"]):
            affected_agents.add("Customer / Marketing")
        if any(w in desc_lower for w in ["fraud", "default", "risk", "delinquency", "solvency", "penalty"]):
            affected_agents.add("Risk")
        if any(w in desc_lower for w in ["regulation", "compliance", "audit", "disclosure", "security", "soc2"]):
            affected_agents.add("Compliance / Quality")

        # Classify baseline findings
        finding_classifications = {}
        for finding_name in ["Market Research Findings", "Financial Feasibility Model", "GTM Commercial Strategy", "Operations Delivery Plan", "Regulatory Compliance Checklist"]:
            if any(term in finding_name.lower() for term in ["market", "gtm"]) and ("Customer / Marketing" in affected_agents or "competitor" in desc_lower or "demand" in desc_lower):
                finding_classifications[finding_name] = "PARTIALLY AFFECTED"
            elif "financial" in finding_name.lower() and "Finance & Economics" in affected_agents:
                finding_classifications[finding_name] = "INVALIDATED"
            elif "operations" in finding_name.lower() and "Operations / Engineering" in affected_agents:
                finding_classifications[finding_name] = "INVALIDATED"
            else:
                finding_classifications[finding_name] = "VALID"

        return {
            "surprise_id": surprise.id,
            "severity": surprise.severity,
            "invalidated_assumptions": invalidated,
            "materially_affected_agents": sorted(list(affected_agents)),
            "finding_classifications": finding_classifications,
            "preserves_unaffected_agents": True
        }
