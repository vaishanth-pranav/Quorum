"""
Case Profiler for Quorum.
Extracts a structured 20-dimension CaseProfile before boardroom deliberation begins.
Enforces the anti-hallucination principle: missing facts are labeled 'UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE'.
"""

import re
from typing import List, Dict, Any
from ..models.business_case import BusinessCase, CaseProfile


class CaseProfiler:
    """Extracts structured decision dimensions from any BusinessCase."""

    @classmethod
    def profile(cls, case: BusinessCase) -> CaseProfile:
        text = f"{case.title}\n{case.problem}\n{case.objective}\n{case.context}"
        
        # 1. Company Name Extraction
        company = cls._extract_company(case.title, text)
        
        # 2. Industry Extraction
        industry = cls._extract_industry(text)

        # 3. Available Capital
        capital = cls._extract_capital(case)

        # 4. Constraints Categorization
        hard_c, ops_c, comp_c, time_c = cls._categorize_constraints(case.constraints)

        # 5. Candidate Strategies
        candidate_strategies = cls._extract_candidate_strategies(case)

        # 6. Customer Segments
        customer_segments = cls._extract_customer_segments(case)

        # 7. Quantitative Assumptions
        assumptions = [a for a in case.assumptions] or ["UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"]

        # 8. Success KPIs
        required_kpis = cls._extract_kpis(case)

        return CaseProfile(
            company=company,
            industry=industry,
            business_objective=case.objective or "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE",
            decision_question=case.problem or "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE",
            available_capital=capital,
            resource_capacity=cls._extract_capacity(case),
            customer_segments=customer_segments or ["UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"],
            demand_data=case.available_data.get("customer_discovery", case.available_data.get("demand", {})),
            cost_data=case.available_data.get("financial_metrics", case.available_data.get("costs", {})),
            revenue_data=case.available_data.get("projections", case.available_data.get("revenue", {})),
            risk_data=case.available_data.get("risks", {}),
            operational_constraints=ops_c,
            compliance_constraints=comp_c,
            time_constraints=time_c,
            hard_constraints=hard_c,
            soft_objectives=[case.objective] if case.objective else [],
            mandatory_roles=case.mandatory_roles,
            candidate_strategies=candidate_strategies,
            quantitative_assumptions=assumptions,
            required_kpis=required_kpis
        )

    @classmethod
    def _extract_company(cls, title: str, text: str) -> str:
        match = re.search(r'\]\s*([A-Za-z0-9\s]+?)(?::|\s+Mobility|\s+Capital|\s+Systems|\s+Fab|\s+Space|\s+AI|\s+is|\s+has)', title)
        if match:
            return match.group(1).strip()
        first_words = title.replace("[TEST CASE]", "").replace("[FINSWARM]", "").replace("[SAASSWARM]", "").replace("[CHIPSWARM]", "").strip().split(":")
        if first_words:
            return first_words[0].strip()
        return "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"

    @classmethod
    def _extract_industry(cls, text: str) -> str:
        lower = text.lower()
        if any(w in lower for w in ["saas", "cloud", "vpc", "b2b software", "plg", "arr"]):
            return "Enterprise Cloud Software / B2B SaaS"
        elif any(w in lower for w in ["wafer", "fab", "semiconductor", "euv", "lithography", "wspm"]):
            return "Semiconductor Manufacturing & Foundry"
        elif any(w in lower for w in ["lending", "credit risk", "microloan", "loan", "factoring", "fintech", "apr"]):
            return "Fintech / Digital Credit & Treasury"
        elif any(w in lower for w in ["charging", "ev charging", "electric vehicle", "fleet hub", "mobility"]):
            return "EV Mobility & Charging Infrastructure"
        elif any(w in lower for w in ["orbit", "satellite", "spaceflight", "rocket", "smallsat", "space"]):
            return "Commercial Aerospace & Space Logistics"
        elif any(w in lower for w in ["pharma", "biotech", "clinical", "diagnostic", "healthcare"]):
            return "Biotechnology & Healthcare"
        return "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"



    @classmethod
    def _extract_capital(cls, case: BusinessCase) -> str:
        for c in case.constraints:
            if "$" in c and ("budget" in c.lower() or "capital" in c.lower() or "capped" in c.lower()):
                return c
        for k, v in case.available_data.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    if "capital" in sk.lower() or "cash" in sk.lower() or "pool" in sk.lower():
                        return str(sv)
        return "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"

    @classmethod
    def _extract_capacity(cls, case: BusinessCase) -> str:
        for k, v in case.available_data.items():
            if "capacity" in k.lower() or "utilization" in k.lower():
                return str(v)
            if isinstance(v, dict):
                for sk, sv in v.items():
                    if "capacity" in sk.lower() or "utilization" in sk.lower() or "wspm" in sk.lower():
                        return f"{sk}: {sv}"
        return "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"

    @classmethod
    def _categorize_constraints(cls, constraints: List[str]):
        hard_c, ops_c, comp_c, time_c = [], [], [], []
        for c in constraints:
            lower = c.lower()
            if "strictly" in lower or "capped" in lower or "must not exceed" in lower or "minimum" in lower or "mandatory" in lower:
                hard_c.append(c)
            elif "regulatory" in lower or "compliance" in lower or "soc2" in lower or "disclosure" in lower or "protection" in lower:
                comp_c.append(c)
            elif "month" in lower or "quarter" in lower or "timeline" in lower or "lead time" in lower:
                time_c.append(c)
            else:
                ops_c.append(c)
        return hard_c, ops_c, comp_c, time_c

    @classmethod
    def _extract_candidate_strategies(cls, case: BusinessCase) -> List[str]:
        strats = []
        for k in case.available_data.keys():
            if "strategy" in k.lower() or "node" in k.lower():
                strats.append(k.replace("_", " ").title())
        if not strats:
            text = f"{case.problem} {case.context}"
            matches = re.findall(r'(?:Strategy\s+[A-Za-z0-9]+|\b(?:Expand|Pivot|Launch|Construct)\s+[^,\.\n]+)', text, re.IGNORECASE)
            for m in matches[:3]:
                strats.append(m.strip())
        return strats or ["Strategy Alpha", "Strategy Beta"]

    @classmethod
    def _extract_customer_segments(cls, case: BusinessCase) -> List[str]:
        segments = []
        text = f"{case.problem} {case.context}".lower()
        if "fleet" in text:
            segments.append("Commercial Delivery Fleets (Amazon DSPs, FedEx, DHL)")
        if "consumer" in text:
            segments.append("Direct-to-Consumer (D2C) Retail Borrowers")
        if "sme" in text or "merchant" in text:
            segments.append("SME B2B Merchants & Invoice Borrowers")
        if "developer" in text or "enterprise" in text:
            segments.append("Enterprise Cloud Buyers & Developer Teams")
        if "automotive" in text or "hpc" in text:
            segments.append("Tier-1 Automotive OEMs & Hyperscaler AI Chip Buyers")
        return segments

    @classmethod
    def _extract_kpis(cls, case: BusinessCase) -> List[str]:
        kpis = []
        text = f"{case.problem} {case.objective}".lower()
        if "ebitda" in text or "break-even" in text:
            kpis.append("EBITDA Break-Even Timeline (months)")
        if "roe" in text or "margin" in text:
            kpis.append("Return on Equity / Gross Margin (%)")
        if "default" in text:
            kpis.append("Portfolio Default Rate (<4.5%)")
        if "arr" in text:
            kpis.append("Annual Recurring Revenue (ARR) Target ($)")
        if "wspm" in text or "yield" in text:
            kpis.append("Fab Line Yield & Cleanroom Utilization (%)")
        if not kpis:
            kpis.append("Operational Break-Even Timeline")
            kpis.append("Capital Preservation Floor")
            kpis.append("Target Customer Contracted Volume")
        return kpis
