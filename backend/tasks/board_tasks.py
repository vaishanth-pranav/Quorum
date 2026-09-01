"""
Task definitions for Quorum Boardroom Collaboration Protocol and Surprise Round Adaptation.
Fully aligned with the QUORUM Master System Prompt:
- Protocol: ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE (-> SURPRISE -> REASSESS -> DECIDE)
- Numerical Discipline & Hard Constraint Enforcement
- Exact 13-Section QUORUM Executive Decision Format
- Anti-Hallucination Labeling (mark missing data as 'NOT PROVIDED IN ACTIVE TEST CASE')
"""

from typing import List, Optional
from crewai import Task, Agent
from ..models.business_case import BusinessCase, SurpriseEvent


class BoardTasks:
    def __init__(self, business_case: BusinessCase):
        self.business_case = business_case
        self.brief_md = business_case.to_brief_markdown()

    # -------------------------------------------------------------------------
    # STAGE 1: ANALYSE
    # -------------------------------------------------------------------------
    def research_task(self, agent: Agent) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — BUSINESS & MARKET RESEARCH]\n"
                f"Analyze the active business case brief solely from provided facts:\n\n"
                f"{self.brief_md}\n\n"
                f"Your task:\n"
                f"1. Extract customer discovery signals, market demand estimates, and competitor positioning.\n"
                f"2. Clearly distinguish between FACT, CALCULATION, ASSUMPTION, and INFERENCE.\n"
                f"3. Mark any missing data explicitly as 'NOT PROVIDED IN ACTIVE TEST CASE'. Never invent market statistics.\n"
                f"4. Deliver a structured Research Report evaluating the candidate strategies against market realities."
            ),
            expected_output=(
                "A structured Business Research Report containing:\n"
                "- Verified Market Dynamics & Case Facts\n"
                "- Competitive Landscape & Moat Analysis\n"
                "- Customer Demand Validation & Discovery Insights\n"
                "- Explicit List of Verified Facts vs. Assumptions vs. Not Provided Data"
            ),
            agent=agent,
        )

    def finance_task(self, agent: Agent, context: Optional[List[Task]] = None) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — FINANCIAL FEASIBILITY & NUMERICAL DISCIPLINE]\n"
                f"Conduct a rigorous financial and capital allocation assessment of the active case:\n\n"
                f"{self.brief_md}\n\n"
                f"Incorporate findings from the Business Research report.\n"
                f"Your task:\n"
                f"1. Extract all numerical inputs and model unit economics, CapEx, OpEx, margins, and cash burn.\n"
                f"2. Enforce all hard financial constraints (budget caps, minimum liquidity, break-even timelines).\n"
                f"3. Calculate exact runway buffers under expected and delayed scenarios.\n"
                f"4. Eliminate or flag any strategy that violates a hard constraint.\n"
                f"5. State your department's ranked financial recommendation."
            ),
            expected_output=(
                "A comprehensive Financial Feasibility Report containing:\n"
                "- Comparative Unit Economics & Margin Calculations\n"
                "- Cash Burn, Runway & CapEx Allocation Breakdown against Budget Cap\n"
                "- Hard Financial Constraints Checked (Pass / Fail)\n"
                "- Sensitivity Analysis & Ranked Recommendation"
            ),
            agent=agent,
            context=context or [],
        )

    def marketing_task(self, agent: Agent, context: Optional[List[Task]] = None) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — COMMERCIAL & GO-TO-MARKET STRATEGY]\n"
                f"Develop a commercial and GTM strategy based strictly on case facts:\n\n"
                f"{self.brief_md}\n\n"
                f"Incorporate findings from the Business Research report.\n"
                f"Your task:\n"
                f"1. Define target customer segmentation, positioning, and value proposition.\n"
                f"2. Quantify Customer Acquisition Cost (CAC), Lifetime Value (LTV), and sales pipeline conversion timelines.\n"
                f"3. Evaluate commercial readiness and required distribution channels.\n"
                f"4. State your department's commercial recommendation."
            ),
            expected_output=(
                "A Go-To-Market & Commercial Strategy Report containing:\n"
                "- Target Segmentation & Value Proposition\n"
                "- Acquisition Channels & Sales Cycle Dynamics\n"
                "- Estimated CAC/LTV & Commercial Economics\n"
                "- Commercial Recommendation & Sales Ramp-up Timeline"
            ),
            agent=agent,
            context=context or [],
        )

    def operations_task(self, agent: Agent, context: Optional[List[Task]] = None) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — OPERATIONS & EXECUTION FEASIBILITY]\n"
                f"Evaluate operational feasibility, supply chain lead times, and capacity constraints:\n\n"
                f"{self.brief_md}\n\n"
                f"Incorporate findings from the Business Research report.\n"
                f"Your task:\n"
                f"1. Evaluate execution feasibility, procurement lead times, and utility/regulatory constraints.\n"
                f"2. Calculate capacity limits, engineering readiness, and operational throughput.\n"
                f"3. Identify physical and supply chain bottlenecks that could delay revenue generation.\n"
                f"4. State your department's operational delivery plan and milestone roadmap."
            ),
            expected_output=(
                "An Operational Feasibility & Delivery Report containing:\n"
                "- Infrastructure, Supply Chain & Lead-Time Analysis\n"
                "- Engineering/Team Capacity & Skill Gap Assessment\n"
                "- Hard Operational Constraints Checked\n"
                "- Operational Recommendation & Phased Deployment Milestones"
            ),
            agent=agent,
            context=context or [],
        )

    def product_task(self, agent: Agent, context: Optional[List[Task]] = None) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — PRODUCT ARCHITECTURE & STRATEGY]\n"
                f"Evaluate product feasibility, feature requirements, and strategic positioning:\n\n"
                f"{self.brief_md}\n\n"
                f"Incorporate findings from Business Research.\n"
                f"Your task:\n"
                f"1. Evaluate product roadmap, feature complexity, and architecture trade-offs.\n"
                f"2. Align product deliverables with customer segment priorities.\n"
                f"3. State your department's product recommendation."
            ),
            expected_output=(
                "A Product Architecture & Strategy Report detailing feature scope and delivery timeline."
            ),
            agent=agent,
            context=context or [],
        )

    def compliance_task(self, agent: Agent, context: Optional[List[Task]] = None) -> Task:
        return Task(
            description=(
                f"[STAGE 1: ANALYSE — REGULATORY COMPLIANCE & QUALITY ASSURANCE]\n"
                f"Evaluate legal, compliance, customer protection, and quality standards:\n\n"
                f"{self.brief_md}\n\n"
                f"Your task:\n"
                f"1. Audit candidate strategies against mandatory compliance and regulatory rules.\n"
                f"2. Flag any non-compliant practice as a hard stop.\n"
                f"3. State required safeguards and audit checklists."
            ),
            expected_output=(
                "A Compliance & Quality Assurance Report detailing regulatory compliance."
            ),
            agent=agent,
            context=context or [],
        )


    # -------------------------------------------------------------------------
    # STAGE 3: CHALLENGE (Adversarial Risk / Reviewer)
    # -------------------------------------------------------------------------
    def risk_challenge_task(self, agent: Agent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE 3: CHALLENGE — ADVERSARIAL RISK REVIEW]\n"
                f"Inspect the actual findings submitted by Research, Finance, Marketing & Sales, and Operations:\n\n"
                f"{self.brief_md}\n\n"
                f"Your task as Chief Risk Officer:\n"
                f"1. Attack weak assumptions, constraint violations, liquidity traps, and operational bottlenecks.\n"
                f"2. Detect inter-departmental contradictions (e.g. Finance CapEx vs Ops delivery lead times, Sales volume vs capacity).\n"
                f"3. Specifically identify the challenged department and recommendation.\n"
                f"4. Cite the exact factual and numerical evidence behind your challenge.\n"
                f"5. Issue a formal demand for defense or revision."
            ),
            expected_output=(
                "A formal Adversarial Boardroom Challenge document detailing:\n"
                "- Target Department Challenged\n"
                "- Specific Recommendation or Assumption Challenged\n"
                "- Factual & Numerical Evidence of Flaw or Cross-Departmental Contradiction\n"
                "- Formal Demand for Defense or Revision"
            ),
            agent=agent,
            context=context,
        )

    # -------------------------------------------------------------------------
    # STAGE 4: RESPONSE (Challenged Department Defense / Revision)
    # -------------------------------------------------------------------------
    def department_response_task(self, agent: Agent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE 4: RESPONSE — DEPARTMENT DEFENSE & REVISION]\n"
                f"Review the formal Adversarial Challenge issued by the Chief Risk Officer:\n\n"
                f"{self.brief_md}\n\n"
                f"Your task:\n"
                f"1. Evaluate the critique.\n"
                f"2. State your definitive VERDICT: [ACCEPT], [REJECT], or [MODIFY].\n"
                f"3. Provide revised calculations, modified allocations, or substantive evidence defending your position.\n"
                f"4. Deliver an updated departmental recommendation with strengthened safeguards."
            ),
            expected_output=(
                "A formal Department Response and Defense/Revision containing:\n"
                "- Responding Department & Verdict (ACCEPT / REJECT / MODIFY)\n"
                "- Substantive Defense & Numerical Reasoning\n"
                "- Revised Recommendation, Updated Assumptions, and Safeguards"
            ),
            agent=agent,
            context=context,
        )

    # -------------------------------------------------------------------------
    # STAGE 5: COMPARE (Boardroom Strategy Comparison Matrix)
    # -------------------------------------------------------------------------
    def strategy_comparison_task(self, agent: Agent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE 5: COMPARE — STRATEGY COMPARISON MATRIX]\n"
                f"Construct an objective Boardroom Strategy Comparison Matrix evaluating at least TWO viable strategies:\n\n"
                f"{self.brief_md}\n\n"
                f"Synthesize department analyses, the Risk Challenge, and the Department Response.\n\n"
                f"Evaluate EACH viable strategy across all core dimensions:\n"
                f"1. Financial outcome & unit economics\n"
                f"2. Risk profile & solvency\n"
                f"3. Liquidity runway & burn\n"
                f"4. Customer impact & market fit\n"
                f"5. Operational feasibility & capacity\n"
                f"6. Compliance & regulatory alignment\n"
                f"7. Implementation lead time\n"
                f"8. Strategic defensibility & competitive moat\n\n"
                f"Enforce objective prioritization: Compliance > Hard Constraints > Liquidity > Feasibility > Value."
            ),
            expected_output=(
                "A comprehensive Strategy Comparison Matrix containing:\n"
                "- Detailed multi-dimensional evaluation for Strategy A and Strategy B\n"
                "- Structured Side-by-Side Comparison Markdown Table\n"
                "- Hard Constraint Compliance Summary for each strategy\n"
                "- Executive Synthesis of Trade-offs for the CEO"
            ),
            agent=agent,
            context=context,
        )

    # -------------------------------------------------------------------------
    # STAGE 6: DECIDE (QUORUM Executive Decision — 13 Sections)
    # -------------------------------------------------------------------------
    def ceo_decision_task(self, agent: Agent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE 6: DECIDE — QUORUM EXECUTIVE DECISION]\n"
                f"Synthesize the entire boardroom proceedings:\n"
                f"- Original department analyses (Research, Finance, Marketing, Operations)\n"
                f"- The Adversarial Risk Challenge\n"
                f"- The Department Defense/Response\n"
                f"- The Strategy Comparison Matrix\n\n"
                f"{self.brief_md}\n\n"
                f"YOUR FINAL OUTPUT MUST STRICTLY USE THE EXACT 13-SECTION 'QUORUM EXECUTIVE DECISION' FORMAT:\n\n"
                f"# QUORUM EXECUTIVE DECISION\n\n"
                f"### 1. Decision\nClearly state the selected strategy and executive mandate.\n\n"
                f"### 2. Target / Scope\nIdentify the target customer, product, market, or operating scope.\n\n"
                f"### 3. Key Calculations\nShow the calculations that materially determine the decision (CapEx, OpEx, margins, break-even, runway).\n\n"
                f"### 4. Constraints Checked\nList every important hard constraint (budget, timeline, regulatory, capacity) and verify compliance (PASS/FAIL).\n\n"
                f"### 5. Approval / Operating Policy\nSpecify relevant thresholds, allocation rules, tranche gates, or operating policies.\n\n"
                f"### 6. Pricing / Financial Plan\nSpecify pricing, budget allocation, expected unit economics, and liquidity reserve floor.\n\n"
                f"### 7. Risk Controls\nIdentify the major risks and concrete operational/financial mitigations.\n\n"
                f"### 8. Go-To-Market / Customer Plan\nSpecify acquisition, channel strategy, sales cycle, and customer management actions.\n\n"
                f"### 9. Implementation Sequence\nGive a phased implementation plan (Phases 1–4) with responsible functions and timing.\n\n"
                f"### 10. Measurable Outcomes\nDefine at least 3 quantitative, measurable business KPIs with targets and timeframes.\n\n"
                f"### 11. Rejected Alternatives\nExplain why competing alternatives were evaluated and rejected.\n\n"
                f"### 12. Key Assumptions\nList governing assumptions that must remain true for success.\n\n"
                f"### 13. Decision Confidence\nState HIGH, MEDIUM, or LOW and explain why based on evidence and constraint checks."
            ),
            expected_output=(
                "A definitive QUORUM Executive Decision Document formatted with all 13 numbered sections explicitly."
            ),
            agent=agent,
            context=context,
        )

    # -------------------------------------------------------------------------
    # SURPRISE ROUND TASKS
    # -------------------------------------------------------------------------
    def surprise_finance_task(self, agent: Agent, surprise_event: SurpriseEvent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE: REASSESS — AFFECTED AGENT (FINANCE)]\n"
                f"A surprise business event has altered operating conditions!\n\n"
                f"{surprise_event.to_brief_markdown()}\n\n"
                f"Original Case Brief:\n{self.brief_md}\n\n"
                f"Your task as CFO:\n"
                f"1. Recalculate capital allocation, cash burn, and runway under updated constraints.\n"
                f"2. Re-test whether the baseline strategy or alternatives satisfy the new hard constraints.\n"
                f"3. Deliver a revised capital allocation recommendation."
            ),
            expected_output=(
                "A Revised Financial Feasibility Report with recalculated runway, burn rate, and capital plan."
            ),
            agent=agent,
            context=context,
        )

    def surprise_operations_task(self, agent: Agent, surprise_event: SurpriseEvent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE: REASSESS — AFFECTED AGENT (OPERATIONS)]\n"
                f"Review the surprise event:\n\n"
                f"{surprise_event.to_brief_markdown()}\n\n"
                f"Your task as Head of Operations:\n"
                f"1. Adjust deployment scope, procurement batches, and field engineering timelines.\n"
                f"2. Eliminate operational bottlenecks created by the shock.\n"
                f"3. Deliver an updated operational milestone roadmap."
            ),
            expected_output=(
                "A Revised Operational Delivery Report with rescoped milestones and lead-time safeguards."
            ),
            agent=agent,
            context=context,
        )

    def surprise_risk_reassess_task(self, agent: Agent, surprise_event: SurpriseEvent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE: REASSESS — ADVERSARIAL RISK REASSESSMENT]\n"
                f"Review the surprise event and updated reports from rerun departments:\n\n"
                f"{surprise_event.to_brief_markdown()}\n\n"
                f"Your task as Chief Risk Officer:\n"
                f"1. Identify which baseline assumptions are now INVALIDATED.\n"
                f"2. Reconstruct the Strategy Comparison Matrix under the new conditions.\n"
                f"3. Stress-test solvency and execution risks for the CEO."
            ),
            expected_output=(
                "A Revised Boardroom Risk Assessment & Updated Strategy Comparison Matrix."
            ),
            agent=agent,
            context=context,
        )

    def surprise_ceo_decision_task(self, agent: Agent, surprise_event: SurpriseEvent, context: List[Task]) -> Task:
        return Task(
            description=(
                f"[STAGE: DECIDE — REVISED QUORUM EXECUTIVE DECISION]\n"
                f"Review the surprise shock, re-run department analyses, and updated risk assessment:\n\n"
                f"{surprise_event.to_brief_markdown()}\n\n"
                f"Deliver the REVISED QUORUM EXECUTIVE DECISION using the 13-section format, explicitly explaining:\n"
                f"- What changed and which previous assumptions became invalid.\n"
                f"- Which agents were reassessed vs what remained valid.\n"
                f"- Whether the previous strategy remained viable, was modified, or replaced.\n"
                f"- Complete 13 sections with updated calculations, constraints, implementation steps, KPIs, and confidence level."
            ),
            expected_output=(
                "A definitive Revised QUORUM Executive Decision Document with all 13 sections updated for the surprise condition."
            ),
            agent=agent,
            context=context,
        )


def create_board_tasks(business_case: BusinessCase) -> BoardTasks:
    return BoardTasks(business_case=business_case)
