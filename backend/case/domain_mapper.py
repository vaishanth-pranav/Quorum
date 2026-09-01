"""
Dynamic Domain Mapping & Capability Assignment Layer.
Analyzes active test cases and maps required roles onto Quorum's 8 core capabilities:
1. business_research
2. finance_economics
3. risk
4. product_strategy
5. operations_engineering
6. customer_marketing
7. compliance_quality
8. ceo

Enforces max 8 agents limit while respecting all test-case mandatory roles.
"""

from typing import List, Dict, Set, Tuple
from ..models.business_case import BusinessCase


CAPABILITY_MAP = {
    # 1. Research
    "business research": "business_research",
    "market research": "business_research",
    "business / market research": "business_research",
    "business intelligence": "business_research",
    "analyst": "business_research",

    # 2. Finance
    "finance": "finance_economics",
    "finance and treasury": "finance_economics",
    "treasury": "finance_economics",
    "cfo": "finance_economics",
    "economics": "finance_economics",
    "finance & economics": "finance_economics",

    # 3. Risk
    "risk": "risk",
    "credit risk": "risk",
    "cro": "risk",
    "risk / reviewer": "risk",
    "risk officer": "risk",
    "reviewer": "risk",

    # 4. Product / Strategy
    "product": "product_strategy",
    "product / strategy": "product_strategy",
    "strategy": "product_strategy",
    "corporate strategy": "product_strategy",
    "product management": "product_strategy",

    # 5. Operations / Engineering
    "operations": "operations_engineering",
    "operations / engineering": "operations_engineering",
    "engineering": "operations_engineering",
    "infrastructure": "operations_engineering",
    "manufacturing": "operations_engineering",
    "supply chain": "operations_engineering",
    "manufacturing + supply chain": "operations_engineering",

    # 6. Customer / Marketing
    "marketing": "customer_marketing",
    "marketing and sales": "customer_marketing",
    "customer / marketing": "customer_marketing",
    "sales": "customer_marketing",
    "cmo": "customer_marketing",
    "commercial": "customer_marketing",
    "customer experience": "customer_marketing",

    # 7. Compliance / Quality / Reliability
    "compliance": "compliance_quality",
    "compliance and customer protection": "compliance_quality",
    "compliance / quality": "compliance_quality",
    "compliance / quality / reliability": "compliance_quality",
    "customer protection": "compliance_quality",
    "quality": "compliance_quality",
    "reliability": "compliance_quality",
    "legal": "compliance_quality",
    "security": "compliance_quality",

    # 8. CEO
    "ceo": "ceo",
    "chief executive officer": "ceo",
    "executive": "ceo",
    "ceo agent": "ceo",
    "executive decision": "ceo",
}


class DomainMapper:
    """Maps runtime case properties into capability assignments."""

    @classmethod
    def resolve_agent_capabilities(cls, business_case: BusinessCase) -> List[Tuple[str, str, str]]:
        """
        Determines the active board composition (4 to 8 agents) based on mandatory roles
        and case requirements, returning (capability_id, custom_role_title, domain_instruction_focus).
        """
        assigned_caps: Set[str] = set()
        active_roles: List[Tuple[str, str, str]] = []

        # 1. Map explicit mandatory roles if specified by test case
        if business_case.mandatory_roles:
            for req_role in business_case.mandatory_roles:
                norm_key = req_role.strip().lower()
                cap = CAPABILITY_MAP.get(norm_key)
                if not cap:
                    for k, v in CAPABILITY_MAP.items():
                        if k in norm_key or norm_key in k:
                            cap = v
                            break
                if not cap:
                    cap = "operations_engineering"  # generic fallback capability

                if cap not in assigned_caps:
                    assigned_caps.add(cap)
                    active_roles.append((cap, req_role, cls._get_domain_focus(cap, business_case)))

        # 2. Always ensure core mandatory perspectives: Research, Finance, Risk, CEO
        default_baseline = [
            ("business_research", "Business & Market Intelligence Analyst"),
            ("finance_economics", "Chief Financial Officer (CFO)"),
            ("customer_marketing", "Chief Marketing & Commercial Officer (CMO)"),
            ("operations_engineering", "Head of Operations & Infrastructure"),
            ("risk", "Chief Risk Officer & Adversarial Reviewer (CRO)"),
            ("ceo", "Chief Executive Officer (CEO)")
        ]

        if not active_roles:
            for cap, title in default_baseline:
                if cap not in assigned_caps:
                    assigned_caps.add(cap)
                    active_roles.append((cap, title, cls._get_domain_focus(cap, business_case)))

        # 3. Always guarantee CEO is present as the final decision maker
        if "ceo" not in assigned_caps:
            assigned_caps.add("ceo")
            active_roles.append(("ceo", "Chief Executive Officer (CEO)", cls._get_domain_focus("ceo", business_case)))

        # 4. Strictly cap at 8 agents max
        return active_roles[:8]

    @classmethod
    def _get_domain_focus(cls, cap: str, case: BusinessCase) -> str:
        text = f"{case.title} {case.problem} {case.context}".lower()
        if "lending" in text or "credit" in text or "finnova" in text or "loan" in text:
            focus_map = {
                "business_research": "Credit market demand, delinquency trends, borrower segments.",
                "finance_economics": "Cost of funds, capital reserve adequacy, net interest margins, loan loss provisions.",
                "risk": "Credit risk underwriting, macro default spikes, consumer indebtedness, portfolio concentration.",
                "product_strategy": "Credit product design, APR structures, embedded merchant APIs.",
                "operations_engineering": "Loan origination systems, automated underwriting APIs, KYC throughput.",
                "customer_marketing": "Borrower CAC, merchant partnership distribution, conversion funnels.",
                "compliance_quality": "Consumer Protection Lending Disclosures, APR caps, fair lending compliance.",
                "ceo": "Capital allocation between credit lines, risk-adjusted ROE, regulatory safety."
            }
            return focus_map.get(cap, "Financial domain analysis.")
        elif "saas" in text or "cloud" in text or "arr" in text or "vpc" in text:
            focus_map = {
                "business_research": "Enterprise cloud market dynamics, developer tool trends, competitive hyperscaler moats.",
                "finance_economics": "SaaS unit economics, ARR growth vs burn rate, gross margin retention, cloud hosting COGS.",
                "risk": "Enterprise sales cycle drag, hyperscaler price wars, high-churn vulnerability.",
                "product_strategy": "Product-led growth (PLG) self-serve tier vs single-tenant dedicated VPC features.",
                "operations_engineering": "Multi-tenant cloud infrastructure scaling, reliability SLAs, site reliability engineering.",
                "customer_marketing": "Developer acquisition, CAC/LTV, enterprise outbound sales pipeline.",
                "compliance_quality": "SOC2 Type II, FedRAMP, data sovereignty, enterprise security audits.",
                "ceo": "Balancing self-serve developer velocity with high-ACV enterprise stability."
            }
            return focus_map.get(cap, "Cloud SaaS domain analysis.")
        elif "chip" in text or "wafer" in text or "fab" in text or "foundry" in text:
            focus_map = {
                "business_research": "Semiconductor supply-demand cycle, automotive ASIC demand, AI packaging premiums.",
                "finance_economics": "Fab fixed cost absorption, wafer contribution margin, CapEx depreciation amortization.",
                "risk": "EUV lithography tool downtime, contract penalty exposure, customer concentration.",
                "product_strategy": "Node roadmap: 5nm advanced EUV packaging vs 28nm mature automotive MCUs.",
                "operations_engineering": "Cleanroom wafer starts per month (WSPM), defect density, yield ramp curves.",
                "customer_marketing": "Automotive Tier-1 OEM long-term contracts vs hyperscaler AI chip buyers.",
                "compliance_quality": "Automotive Grade AEC-Q100 reliability qualification, defect per million (DPM) standards.",
                "ceo": "Capacity allocation maximizing contribution margin while guaranteeing OEM volume commitments."
            }
            return focus_map.get(cap, "Semiconductor fab domain analysis.")
        else:
            return "General business strategy, mathematical verification, constraint checking, and executive decision synthesis."
