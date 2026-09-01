"""
Pydantic data models for Quorum business case inputs, case profiling, constraint evaluation,
collaboration stages, surprise round adaptations, and structured multi-domain outputs.
"""

from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


# -----------------------------------------------------------------------------
# CORE BUSINESS CASE MODEL
# -----------------------------------------------------------------------------

class BusinessCase(BaseModel):
    """
    Generic BusinessCase input model that accepts any business scenario at runtime.
    """
    title: str = Field(..., description="Title of the business case or challenge")
    problem: str = Field(..., description="Core problem statement facing the organization")
    objective: str = Field(..., description="Primary business objective to achieve")
    context: str = Field(..., description="Background company & market context")
    constraints: List[str] = Field(default_factory=list, description="Budget, timeline, regulatory or operational constraints")
    available_data: Dict[str, Any] = Field(default_factory=dict, description="Key data points, metrics, financial figures")
    assumptions: List[str] = Field(default_factory=list, description="Initial documented baseline assumptions")
    mandatory_roles: List[str] = Field(default_factory=list, description="Optional explicit mandatory agent roles specified by test case")

    def to_brief_markdown(self) -> str:
        """Render the business case into a clean, structured Markdown brief for agents."""
        constraints_list = "\n".join([f"- {c}" for c in self.constraints]) or "- None explicitly specified"
        assumptions_list = "\n".join([f"- {a}" for a in self.assumptions]) or "- None provided"

        data_formatted = []
        for k, v in self.available_data.items():
            if isinstance(v, dict):
                sub_items = ", ".join([f"{sk}: {sv}" for sk, sv in v.items()])
                data_formatted.append(f"- **{k}**: {sub_items}")
            elif isinstance(v, list):
                data_formatted.append(f"- **{k}**: {', '.join(str(item) for item in v)}")
            else:
                data_formatted.append(f"- **{k}**: {v}")
        data_text = "\n".join(data_formatted) or "- No quantitative data provided"

        return f"""# BUSINESS CASE BRIEF: {self.title}

## 1. Problem Statement
{self.problem}

## 2. Strategic Objective
{self.objective}

## 3. Background & Market Context
{self.context}

## 4. Key Constraints
{constraints_list}

## 5. Available Quantitative & Operational Data
{data_text}

## 6. Documented Baseline Assumptions
{assumptions_list}
"""


# -----------------------------------------------------------------------------
# CASE PROFILE MODEL (20 EXTRACTED DIMENSIONS)
# -----------------------------------------------------------------------------

class CaseProfile(BaseModel):
    """
    Structured Case Profile extracted before boardroom proceedings start.
    Missing data points are explicitly marked 'UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE'.
    """
    company: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    industry: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    business_objective: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    decision_question: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    available_capital: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    resource_capacity: str = Field(default="UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")
    customer_segments: List[str] = Field(default_factory=list)
    demand_data: Dict[str, Any] = Field(default_factory=dict)
    cost_data: Dict[str, Any] = Field(default_factory=dict)
    revenue_data: Dict[str, Any] = Field(default_factory=dict)
    risk_data: Dict[str, Any] = Field(default_factory=dict)
    operational_constraints: List[str] = Field(default_factory=list)
    compliance_constraints: List[str] = Field(default_factory=list)
    time_constraints: List[str] = Field(default_factory=list)
    hard_constraints: List[str] = Field(default_factory=list)
    soft_objectives: List[str] = Field(default_factory=list)
    mandatory_roles: List[str] = Field(default_factory=list)
    candidate_strategies: List[str] = Field(default_factory=list)
    quantitative_assumptions: List[str] = Field(default_factory=list)
    required_kpis: List[str] = Field(default_factory=list)

    def to_markdown(self) -> str:
        hard_c = "\n".join([f"- [HARD] {c}" for c in self.hard_constraints]) or "- None provided"
        ops_c = "\n".join([f"- {c}" for c in self.operational_constraints]) or "- None provided"
        comp_c = "\n".join([f"- {c}" for c in self.compliance_constraints]) or "- None provided"
        strats = "\n".join([f"- {s}" for s in self.candidate_strategies]) or "- None provided"
        roles = ", ".join(self.mandatory_roles) or "Standard Boardroom Roles"

        return f"""# 📋 STRUCTURED CASE PROFILE
- **Company:** {self.company}
- **Industry:** {self.industry}
- **Objective:** {self.business_objective}
- **Decision Question:** {self.decision_question}
- **Available Capital:** {self.available_capital}
- **Resource Capacity:** {self.resource_capacity}
- **Mandatory Roles:** {roles}

### Candidate Strategies:
{strats}

### Hard Constraints (Non-Negotiable):
{hard_c}

### Operational & Compliance Constraints:
{ops_c}
{comp_c}
"""


# -----------------------------------------------------------------------------
# CONSTRAINT EVALUATION & CALCULATION MODELS
# -----------------------------------------------------------------------------

class ConstraintStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    INFEASIBLE = "INFEASIBLE"


class ConstraintEvaluation(BaseModel):
    name: str = Field(..., description="Constraint name or description")
    limit_value: str = Field(..., description="Threshold limit (e.g. Max $10M CapEx, Max 5% Default Rate)")
    evaluated_value: str = Field(..., description="Calculated actual value under this strategy")
    is_hard: bool = Field(default=True, description="Whether this is a non-negotiable hard constraint")
    status: ConstraintStatus = Field(default=ConstraintStatus.PASS, description="PASS, FAIL, or INFEASIBLE")
    notes: Optional[str] = Field(None, description="Analytical reasoning or breach explanation")


class StrategyMathResult(BaseModel):
    strategy_name: str
    total_cost: float
    total_revenue: float
    gross_margin_pct: float
    cash_runway_months: float
    break_even_month: Optional[int]
    constraint_evaluations: List[ConstraintEvaluation] = Field(default_factory=list)
    is_feasible: bool = True
    infeasibility_reasons: List[str] = Field(default_factory=list)


# -----------------------------------------------------------------------------
# BOARDROOM PROTOCOL & DEBATE MODELS
# -----------------------------------------------------------------------------

class ChallengeVerdict(str, Enum):
    ACCEPT = "ACCEPT"
    REJECT = "REJECT"
    MODIFY = "MODIFY"


class BoardroomChallenge(BaseModel):
    target_department: str = Field(..., description="The department agent being challenged")
    target_recommendation: str = Field(..., description="The specific recommendation or assumption under dispute")
    flaw_type: str = Field(..., description="Type of flaw: Contradiction, Unsupported Assumption, Execution Risk, Capital Vulnerability")
    critique_evidence: str = Field(..., description="Detailed factual evidence and data citation justifying the challenge")
    response_request: str = Field(..., description="Concrete clarification or revision requested from the challenged agent")


class DepartmentResponse(BaseModel):
    responding_department: str = Field(..., description="Department providing the response")
    verdict: ChallengeVerdict = Field(..., description="Whether the challenge is accepted, rejected, or modified")
    evidence_and_rationale: str = Field(..., description="Detailed explanation, defense, or concession")
    revised_recommendation_or_assumptions: str = Field(..., description="Updated figures, altered roadmap, or defended position")


class StrategyProfile(BaseModel):
    strategy_name: str = Field(..., description="Name of strategy")
    business_value: str = Field(..., description="Expected strategic value, revenue trajectory, and competitive moat")
    financial_viability: str = Field(..., description="CapEx/OpEx, gross margin, payback timeline, EBITDA break-even")
    market_customer_fit: str = Field(..., description="Customer adoption sentiment, demand validation, CAC/LTV dynamics")
    operational_feasibility: str = Field(..., description="Delivery timeline, supply chain lead times, team capabilities")
    risk_level: str = Field(..., description="Key execution and solvency risks")
    is_feasible: bool = Field(default=True, description="Whether all hard constraints are satisfied")
    major_assumptions: List[str] = Field(default_factory=list, description="Core governing assumptions")


class StrategyComparisonMatrix(BaseModel):
    strategies: List[StrategyProfile] = Field(..., min_items=2, description="At least two evaluated viable strategies")
    comparative_summary: str = Field(..., description="Executive synthesis of comparative strengths and weaknesses")


class AlternativeOption(BaseModel):
    name: str = Field(..., description="Name or summary of the rejected strategy")
    reason_for_rejection: str = Field(..., description="Substantive reason why this alternative was rejected")


class ImplementationStep(BaseModel):
    step_number: int = Field(..., description="Sequential step number or phase")
    action: str = Field(..., description="Concrete action item")
    responsible_department: str = Field(..., description="Department lead (Finance, Ops, Marketing, etc.)")
    timeframe: Optional[str] = Field(None, description="Estimated duration or target quarter")


class BusinessKPI(BaseModel):
    metric: str = Field(..., description="KPI name or metric description")
    target: str = Field(..., description="Target value or measurable benchmark")
    timeframe: str = Field(..., description="Measurement timeframe (e.g. Q2, Year 1)")


class CEODecisionOutput(BaseModel):
    selected_decision: str = Field(..., description="The chosen strategic decision and core rationale")
    evidence_used: List[str] = Field(..., description="Key pieces of evidence from department agents")
    how_challenge_affected_decision: str = Field(..., description="How debate reshaped or validated the decision")
    rejected_alternatives: List[AlternativeOption] = Field(default_factory=list)
    trade_offs: List[str] = Field(...)
    risks: List[str] = Field(...)
    assumptions: List[str] = Field(...)
    implementation_steps: List[ImplementationStep] = Field(...)
    kpis: List[BusinessKPI] = Field(..., min_items=3)


# -----------------------------------------------------------------------------
# SURPRISE ROUND MODELS
# -----------------------------------------------------------------------------

class SurpriseType(str, Enum):
    BUDGET_REDUCTION = "budget_reduction"
    DEMAND_DROP = "demand_drop"
    COMPETITOR_ENTRY = "competitor_entry"
    COST_INCREASE = "cost_increase"
    SUPPLY_DISRUPTION = "supply_disruption"
    REGULATORY_CHANGE = "regulatory_change"
    FRAUD_SPIKE = "fraud_spike"
    YIELD_DROP = "yield_drop"
    UNFORESEEN_SHOCK = "unforeseen_shock"


class SurpriseEvent(BaseModel):
    id: str = Field(..., description="Unique identifier for the surprise event")
    type: SurpriseType = Field(default=SurpriseType.UNFORESEEN_SHOCK, description="Categorical classification")
    description: str = Field(..., description="Detailed description of the unexpected change in conditions")
    severity: str = Field(default="HIGH", description="Impact severity: LOW, MEDIUM, HIGH, CRITICAL")
    affected_departments: List[str] = Field(..., description="Departments materially impacted that must be re-run")
    changed_assumptions: List[str] = Field(..., description="List of baseline assumptions that are invalidated or changed")
    new_numerical_constraints: Dict[str, Any] = Field(default_factory=dict, description="New numerical ceilings, floors, or costs")

    def to_brief_markdown(self) -> str:
        depts = ", ".join(self.affected_departments)
        assumptions = "\n".join([f"- {a}" for a in self.changed_assumptions])
        type_str = self.type.value if hasattr(self.type, 'value') else str(self.type)
        return f"""# 🚨 SURPRISE EVENT INGESTION: [{type_str.upper()}]
**Event ID:** {self.id} | **Severity:** {self.severity}

## 1. Description of Change
{self.description}

## 2. Materially Affected Departments
{depts}

## 3. Invalidated / Altered Assumptions
{assumptions}
"""


class RevisedCEODecisionOutput(BaseModel):
    what_changed: str = Field(..., description="Summary of the surprise event and altered operating conditions")
    invalidated_assumptions: List[str] = Field(..., description="Previous baseline assumptions that became invalid")
    rerun_departments: List[str] = Field(..., description="List of department agents that were re-run")
    previous_strategy_viable: bool = Field(..., description="Whether the baseline strategy remains viable")
    selected_decision: str = Field(..., description="Definitive revised strategic decision")
    decision_change_rationale: str = Field(..., description="Why the decision changed or remained stable")
    new_risks: List[str] = Field(..., description="New risks introduced by the surprise event")
    new_assumptions: List[str] = Field(..., description="New governing assumptions that must now be tracked")
    updated_implementation_steps: List[ImplementationStep] = Field(...)
    updated_kpis: List[BusinessKPI] = Field(..., min_items=3)


# -----------------------------------------------------------------------------
# BENCHMARK TEST FIXTURES ACROSS MULTIPLE BUSINESS DOMAINS
# -----------------------------------------------------------------------------

# 1. Mobility Infrastructure (Default Baseline)
DUMMY_BUSINESS_CASE = BusinessCase(
    title="[TEST CASE] AeroCharge Mobility: Fleet Charging Hubs vs Enterprise SaaS Expansion",
    problem="AeroCharge Mobility is experiencing slowing growth in legacy hardware sales (declined 12% YoY). The company has $15M in available capital and must choose between two distinct strategic expansion vectors to achieve sustainable profitability within 18 months, while competition is intensifying from well-funded incumbent energy providers.",
    objective="Select and commit to one primary growth vector for the next 18 months that maximizes return on capital, reaches positive operating cash flow within 12 months, and establishes a defensible competitive moat.",
    context="AeroCharge is a Series B mobility infrastructure firm with 120 employees. The executive board is split between Strategy Alpha (Construct proprietary Ultra-Fast Charging Hubs in 8 Tier-1 urban logistics corridors) and Strategy Beta (Pivot to Enterprise Charging Management Software SaaS platform).",
    constraints=[
        "Total capital expenditure budget capped strictly at $15M for Phase 1.",
        "Must reach EBITDA break-even within 14 months.",
        "Engineering team is currently 35 engineers with strong IoT/firmware skills but limited B2B enterprise software sales talent.",
        "Regulatory grid connection lead time for physical charging hubs currently averages 6-9 months."
    ],
    available_data={
        "financial_metrics": {
            "current_cash_reserves": "$15.0M",
            "monthly_cash_burn": "$450K",
            "hardware_gross_margin": "18%",
            "projected_saas_gross_margin": "78%",
            "projected_hub_gross_margin": "42%"
        },
        "strategy_alpha_hub_projections": {
            "capex_per_hub": "$1.4M (8 hubs = $11.2M total CapEx)",
            "ramp_up_time": "9-12 months per hub",
            "projected_year1_revenue": "$6.8M",
            "projected_year2_revenue": "$18.5M",
            "key_risk": "Grid delay and high upfront capital lock-in"
        },
        "strategy_beta_saas_projections": {
            "rd_and_sales_investment": "$4.5M",
            "target_annual_contract_value": "$120K / enterprise client",
            "sales_cycle": "6-9 months",
            "projected_year1_revenue": "$3.2M",
            "projected_year2_revenue": "$12.0M",
            "key_risk": "Intense software competition from ChargePoint and Siemens, low existing software sales pipeline"
        },
        "customer_discovery": {
            "interviews_conducted": "24 fleet managers",
            "hub_demand_sentiment": "85% urgent demand for dedicated overnight depot hubs",
            "software_demand_sentiment": "60% already using legacy software or unwilling to switch without bundled hardware"
        }
    },
    assumptions=[
        "Electric delivery van adoption among urban parcel carriers will grow at least 30% YoY.",
        "Commercial charging electricity tariffs will average $0.12/kWh in target logistics corridors.",
        "Lead time for high-power DC fast-charging transformers will not exceed 24 weeks."
    ]
)

DUMMY_SURPRISE_EVENT = SurpriseEvent(
    id="SURPRISE-001-BUDGET-CUT",
    type=SurpriseType.BUDGET_REDUCTION,
    description="Board of Directors and Lead Investors mandate an immediate 30% reduction in available launch capital (available budget slashed from $15.0M to $10.5M). The company must still achieve EBITDA neutrality within 14 months.",
    severity="CRITICAL",
    affected_departments=["Finance (CFO)", "Operations"],
    changed_assumptions=[
        "Total capital expenditure budget is now capped strictly at $10.5M (was $15.0M).",
        "Available capital cushion for cost overruns or delay-induced burn is reduced by $4.5M."
    ],
    new_numerical_constraints={"max_budget": 10500000.0}
)


# 2. FINSWARM (Fintech / Lending)
FINSWARM_CASE = BusinessCase(
    title="[FINSWARM] FinNova Capital: Direct Consumer Micro-Lending vs SME Embedded Lending",
    problem="FinNova Capital has $25M in balance sheet lending capital. High-interest macro environment is increasing default risk in unsecured consumer loans, while SME B2B merchants are requesting embedded invoice factoring credit lines.",
    objective="Allocate lending capital across credit products to achieve >15% Return on Equity (ROE) while capping portfolio default rate strictly below 4.5% and maintaining compliance with consumer protection mandates.",
    context="FinNova operates a digital credit scoring engine. Board members disagree between Strategy A (Expand D2C Personal Loans with 24% APR) and Strategy B (Launch SME Embedded B2B Invoicing Credit at 14% APR with merchant platform integrations).",
    constraints=[
        "Total lending capital strictly capped at $25.0M.",
        "Maximum portfolio default rate must not exceed 4.5%.",
        "Must maintain minimum regulatory capital liquidity reserve of $5.0M.",
        "Must comply strictly with Consumer Protection Lending Disclosure regulations."
    ],
    available_data={
        "treasury_metrics": {
            "total_lending_pool": "$25.0M",
            "cost_of_funds": "5.2%",
            "liquidity_reserve_floor": "$5.0M"
        },
        "strategy_consumer_microloans": {
            "allocated_capital": "$20.0M",
            "gross_apr": "24.0%",
            "expected_default_rate": "5.8%",
            "customer_acquisition_cost": "$65/borrower",
            "monthly_origination_volume": "$2.5M"
        },
        "strategy_sme_embedded_factoring": {
            "allocated_capital": "$18.0M",
            "gross_apr": "14.5%",
            "expected_default_rate": "1.9%",
            "customer_acquisition_cost": "$4,200/merchant partner",
            "platform_integration_lead_time": "3 months"
        }
    },
    assumptions=[
        "Consumer loss rates will remain within historical tolerance under current scoring models.",
        "SME invoice default risk is collateralized by merchant platform receivable escrows."
    ],
    mandatory_roles=[
        "Business Research",
        "Finance and Treasury",
        "Credit Risk",
        "Marketing and Sales",
        "Compliance and Customer Protection",
        "CEO"
    ]
)

FINSWARM_SURPRISE = SurpriseEvent(
    id="SURPRISE-FIN-001-CREDIT-SPIKE",
    type=SurpriseType.COST_INCREASE,
    description="Macroeconomic credit shock: Consumer loan delinquency rates surge across the industry, driving FinNova consumer default rates from 5.8% to 9.2%. SME invoice loss rates remain stable at 2.1%.",
    severity="CRITICAL",
    affected_departments=["Risk Agent", "Finance & Economics Agent"],
    changed_assumptions=[
        "Consumer microloan default rate is now 9.2% (violates the 4.5% hard ceiling).",
        "Expected net yield on D2C consumer portfolio is negative after loss write-downs."
    ],
    new_numerical_constraints={"max_default_rate": 0.045}
)

# 3. SAASSWARM (Cloud Enterprise Software)
SAASSWARM_CASE = BusinessCase(
    title="[SAASSWARM] CloudScale Systems: Self-Serve Product-Led Growth vs Enterprise Dedicated VPC",
    problem="CloudScale Systems (AI database orchestration) generates $12M ARR with 90% YoY growth. Enterprise security leaders require single-tenant dedicated VPC deployments, while developers demand an automated, credit-card self-serve tier.",
    objective="Select growth strategy to scale from $12M to $25M ARR within 12 months while keeping cloud infrastructure COGS under 25% of revenue and net revenue retention (NRR) above 120%.",
    context="Engineering team has 40 developers. Expanding dedicated VPCs requires hiring solutions architects and compliance certifications (SOC2 Type II, FedRAMP), whereas self-serve requires self-healing multi-tenant infrastructure.",
    constraints=[
        "Total expansion engineering and GTM budget capped at $6.0M.",
        "Cloud hosting COGS must not exceed 25% of recognized revenue.",
        "Enterprise contracts require mandatory SOC2 compliance certification.",
        "Cash burn must not exceed $350K/month."
    ],
    available_data={
        "saas_metrics": {
            "current_arr": "$12.0M",
            "gross_margin": "78%",
            "net_revenue_retention": "128%",
            "annual_burn_rate": "$3.6M"
        },
        "strategy_self_serve_plg": {
            "investment_required": "$3.8M",
            "target_developer_signups": "50,000 / year",
            "free_to_paid_conversion": "3.5%",
            "projected_arr_addition": "$7.5M",
            "cloud_cogs_margin": "18%"
        },
        "strategy_enterprise_dedicated_vpc": {
            "investment_required": "$5.2M",
            "target_enterprise_deals": "40 clients @ $250K ACV",
            "sales_cycle_length": "7-9 months",
            "projected_arr_addition": "$10.0M",
            "cloud_cogs_margin": "28%"
        }
    },
    assumptions=[
        "Developer conversion rates from open-source to self-serve tier will stay above 3.0%.",
        "Enterprise sales pipeline will convert within 8 months of SOC2 audit completion."
    ],
    mandatory_roles=[
        "Business / Market Research",
        "Finance & Economics",
        "Product / Strategy",
        "Operations / Engineering",
        "Customer / Marketing",
        "Compliance / Quality",
        "CEO"
    ]
)

SAASSWARM_SURPRISE = SurpriseEvent(
    id="SURPRISE-SAAS-001-COMPETITOR-PRICE-WAR",
    type=SurpriseType.COMPETITOR_ENTRY,
    description="Market incumbent hyperscaler launches a competing managed service and slashes developer pricing by 40%, increasing self-serve user churn by 25%. Enterprise demand for secure, isolated dedicated VPCs remains unaffected.",
    severity="HIGH",
    affected_departments=["Product / Strategy Agent", "Customer / Marketing Agent", "Finance & Economics Agent"],
    changed_assumptions=[
        "Self-serve conversion rate drops from 3.5% to 1.8%.",
        "Self-serve annual customer churn increases from 8% to 33%."
    ]
)

# 4. CHIPSWARM (Semiconductor Foundry Capacity)
CHIPSWARM_CASE = BusinessCase(
    title="[CHIPSWARM] SilicoFoundry Fab 7: 5nm HPC AI Accelerators vs 28nm Automotive Microcontrollers",
    problem="SilicoFoundry Fab 7 has 20,000 wafer-starts-per-month (WSPM) cleanroom capacity. Global shortage in automotive chips contrasts with unprecedented margin premiums for advanced 5nm High-Performance Computing (HPC) AI accelerators.",
    objective="Allocate fab line capacity across 5nm advanced packaging vs 28nm mature nodes to maximize total contribution margin while guaranteeing long-term automotive OEM volume commitments.",
    context="5nm yields currently average 68% with $14,000/wafer selling price, while 28nm mature nodes yield 96% with $3,200/wafer selling price and multi-year supply penalties.",
    constraints=[
        "Total cleanroom production capacity strictly capped at 20,000 WSPM.",
        "Mandatory automotive OEM contractual minimum commitment: 8,000 WSPM of 28nm wafers (failure triggers $50M penalty).",
        "Advanced EUV lithography tool maintenance downtime capped at 8% per quarter.",
        "Defect density on 5nm line must maintain wafer yield above 60%."
    ],
    available_data={
        "fab_capacity_metrics": {
            "total_monthly_wafers": "20,000 WSPM",
            "cleanroom_utilization": "94%",
            "monthly_operating_fixed_cost": "$45.0M"
        },
        "node_5nm_hpc_economics": {
            "selling_price_per_wafer": "$14,000",
            "variable_cost_per_wafer": "$5,200",
            "current_yield": "68%",
            "max_euv_capacity": "12,000 WSPM"
        },
        "node_28nm_automotive_economics": {
            "selling_price_per_wafer": "$3,200",
            "variable_cost_per_wafer": "$1,100",
            "current_yield": "96%",
            "contractual_minimum_commitment": "8,000 WSPM"
        }
    },
    assumptions=[
        "5nm die yield will ramp from 68% to 75% over the next 6 months.",
        "Automotive OEM Tier-1 buyers will accept long-term index pricing."
    ],
    mandatory_roles=[
        "Business / Market Research",
        "Finance & Economics",
        "Risk Agent",
        "Operations / Engineering",
        "Customer / Marketing",
        "Compliance / Quality / Reliability",
        "CEO"
    ]
)

CHIPSWARM_SURPRISE = SurpriseEvent(
    id="SURPRISE-CHIP-001-EUV-TOOL-OUTAGE",
    type=SurpriseType.SUPPLY_DISRUPTION,
    description="Critical EUV optics laser failure on Line 1 reduces advanced 5nm wafer throughput by 35% (max 5nm capacity drops from 12,000 to 7,800 WSPM). Mature 28nm DUV lines operate normally at 100% capacity.",
    severity="CRITICAL",
    affected_departments=["Operations / Engineering Agent", "Finance & Economics Agent", "Risk Agent"],
    changed_assumptions=[
        "5nm EUV throughput is capped at 7,800 WSPM (was 12,000 WSPM).",
        "Fixed fab operating costs remain $45.0M/month."
    ],
    new_numerical_constraints={"max_5nm_wspm": 7800.0}
)
