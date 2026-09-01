"""
Boardroom Crew Workflow Orchestrator for Quorum.
Coordinates the complete Boardroom Protocol across Baseline and Surprise Rounds:
ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE -> SURPRISE -> REASSESS -> DECIDE
Integrates CaseProfiler, CalculationEngine, ConstraintValidator, and ImpactMapper.
Preserves both Baseline and Revised CEO Decisions in persistent traces.
"""

from typing import Dict, Any, Optional, List
from crewai import Crew, Process, LLM

from ..config import get_llm, is_verbose
from ..models.business_case import BusinessCase, SurpriseEvent, DUMMY_SURPRISE_EVENT, CaseProfile
from ..case.case_profiler import CaseProfiler
from ..engine.calculator import CalculationEngine
from ..engine.constraint_validator import ConstraintValidator
from ..engine.strategy_evaluator import StrategyEvaluator
from ..surprise.impact_mapper import ImpactMapper
from ..agents.board_agents import BoardAgents
from ..tasks.board_tasks import BoardTasks
from ..trace.trace_manager import TraceManager, TraceStage


class BoardroomCrew:
    """
    Orchestrates the adaptive boardroom swarm (strictly <= 8 agents) across Baseline and Surprise Rounds:
    1. PROFILE: Extracts structured 20-dimension CaseProfile
    2. ANALYSE: Specialists independently analyze domain dimensions
    3. SHARE: Transparent distribution of department findings to boardroom state
    4. CHALLENGE: Chief Risk Officer issues targeted evidence-based challenge
    5. RESPONSE: Challenged department defends or revises assumptions
    6. COMPARE: Evaluates viable strategies via dynamic Strategy Comparison Matrix
    7. DECIDE: CEO issues definitive QUORUM Executive Decision (Baseline Decision)
    8. SURPRISE: Ingests mid-run business disruption event
    9. REASSESS: Re-runs only materially affected agents, CRO reassessment, updated strategy comparison
    10. DECIDE: CEO issues Revised QUORUM Executive Decision (Baseline decision preserved)
    """

    def __init__(self, business_case: BusinessCase, llm: Optional[LLM] = None):
        self.business_case = business_case
        self.profile = CaseProfiler.profile(business_case)
        self.llm = llm or get_llm()
        self.trace_manager = TraceManager(business_case=business_case)
        self.agent_factory = BoardAgents(llm=self.llm, business_case=business_case)
        self.task_factory = BoardTasks(business_case=business_case)

    def assemble_active_agents(self) -> List[Any]:
        """Assembles the board agents based on mandatory roles and case requirements (<= 8 agents)."""
        agents = self.agent_factory.assemble_board(case=self.business_case, profile=self.profile)
        return agents[:8]

    def build_baseline_crew(self) -> Crew:
        """
        Constructs the baseline CrewAI multi-agent crew.
        """
        research_agent = self.agent_factory.business_research_agent()
        finance_agent = self.agent_factory.finance_agent()
        marketing_agent = self.agent_factory.marketing_sales_agent()
        operations_agent = self.agent_factory.operations_agent()
        risk_agent = self.agent_factory.risk_reviewer_agent()
        ceo_agent = self.agent_factory.ceo_agent()

        task_research = self.task_factory.research_task(research_agent)
        task_finance = self.task_factory.finance_task(finance_agent, context=[task_research])
        task_marketing = self.task_factory.marketing_task(marketing_agent, context=[task_research])
        task_operations = self.task_factory.operations_task(operations_agent, context=[task_research])

        task_challenge = self.task_factory.risk_challenge_task(
            risk_agent,
            context=[task_research, task_finance, task_marketing, task_operations]
        )

        task_response = self.task_factory.department_response_task(
            finance_agent,
            context=[task_research, task_finance, task_operations, task_challenge]
        )

        task_compare = self.task_factory.strategy_comparison_task(
            risk_agent,
            context=[task_research, task_finance, task_marketing, task_operations, task_challenge, task_response]
        )

        task_decide = self.task_factory.ceo_decision_task(
            ceo_agent,
            context=[task_research, task_finance, task_marketing, task_operations, task_challenge, task_response, task_compare]
        )

        crew = Crew(
            agents=[
                research_agent,
                finance_agent,
                marketing_agent,
                operations_agent,
                risk_agent,
                ceo_agent
            ],
            tasks=[
                task_research,
                task_finance,
                task_marketing,
                task_operations,
                task_challenge,
                task_response,
                task_compare,
                task_decide
            ],
            process=Process.sequential,
            verbose=is_verbose(),
        )

        return crew

    # Backward compatibility alias
    def build_crew(self) -> Crew:
        return self.build_baseline_crew()

    def run(self) -> Dict[str, Any]:
        """
        Executes the live baseline multi-agent swarm using configured LLM.
        """
        crew = self.build_baseline_crew()
        crew_result = crew.kickoff()
        final_output_str = str(crew_result)

        # Record events into trace
        for i, task in enumerate(crew.tasks):
            agent_role = getattr(task.agent, 'role', f'Agent_{i+1}')
            agent_name = agent_role.split('(')[0].strip() if '(' in agent_role else agent_role
            task_desc = task.description.split('\n')[0] if task.description else f'Task_{i+1}'
            task_output = str(getattr(task, 'output', 'Completed successfully.'))

            if i < 4:
                stage = TraceStage.ANALYSE
            elif i == 4:
                stage = TraceStage.CHALLENGE
            elif i == 5:
                stage = TraceStage.RESPONSE
            elif i == 6:
                stage = TraceStage.COMPARE
            else:
                stage = TraceStage.DECIDE

            self.trace_manager.record_event(
                stage=stage,
                agent_name=agent_name,
                agent_role=agent_role,
                task_name=task_desc,
                input_context=f"Context from {len(task.context or [])} upstream tasks" if task.context else "Case Brief",
                output=task_output
            )

        self.trace_manager.set_baseline_decision(final_output_str)
        trace_file = self.trace_manager.save_trace()

        return {
            "baseline_decision": final_output_str,
            "final_decision": final_output_str,
            "trace_file": str(trace_file),
            "trace_manager": self.trace_manager,
            "crew_output": final_output_str,
        }

    def adapt_to_surprise(self, surprise_event: Optional[SurpriseEvent] = None) -> Dict[str, Any]:
        """
        Executes the live Surprise Round using the LLM.
        """
        surprise = surprise_event or DUMMY_SURPRISE_EVENT

        # 1. Run baseline if not yet executed
        if not self.trace_manager.baseline_decision_raw:
            self.run()

        # 2. Record SURPRISE stage
        self.trace_manager.record_surprise_event(surprise)

        # 3. Assemble surprise tasks
        finance_agent = self.agent_factory.finance_agent()
        operations_agent = self.agent_factory.operations_agent()
        risk_agent = self.agent_factory.risk_reviewer_agent()
        ceo_agent = self.agent_factory.ceo_agent()

        task_surp_finance = self.task_factory.surprise_finance_task(finance_agent, surprise_event=surprise, context=[])
        task_surp_ops = self.task_factory.surprise_operations_task(operations_agent, surprise_event=surprise, context=[])
        task_surp_risk = self.task_factory.surprise_risk_reassess_task(
            risk_agent,
            surprise_event=surprise,
            context=[task_surp_finance, task_surp_ops]
        )
        task_surp_ceo = self.task_factory.surprise_ceo_decision_task(
            ceo_agent,
            surprise_event=surprise,
            context=[task_surp_finance, task_surp_ops, task_surp_risk]
        )

        surprise_crew = Crew(
            agents=[finance_agent, operations_agent, risk_agent, ceo_agent],
            tasks=[task_surp_finance, task_surp_ops, task_surp_risk, task_surp_ceo],
            process=Process.sequential,
            verbose=is_verbose(),
        )

        surprise_result = surprise_crew.kickoff()
        revised_output_str = str(surprise_result)

        # Record rerun tasks
        for i, task in enumerate(surprise_crew.tasks):
            agent_role = getattr(task.agent, 'role', f'Agent_{i+1}')
            agent_name = agent_role.split('(')[0].strip() if '(' in agent_role else agent_role
            task_desc = task.description.split('\n')[0] if task.description else f'Task_{i+1}'
            task_output = str(getattr(task, 'output', 'Completed successfully.'))

            stage = TraceStage.DECIDE if i == len(surprise_crew.tasks) - 1 else TraceStage.REASSESS
            self.trace_manager.record_event(
                stage=stage,
                agent_name=agent_name,
                agent_role=agent_role,
                task_name=task_desc,
                input_context=f"Surprise Shock Context: {surprise.id}",
                output=task_output
            )

        self.trace_manager.set_revised_decision(revised_output_str)
        trace_file = self.trace_manager.save_trace()

        return {
            "baseline_decision": self.trace_manager.baseline_decision_raw,
            "revised_decision": revised_output_str,
            "surprise_event": surprise,
            "trace_file": str(trace_file),
            "trace_manager": self.trace_manager,
            "crew_output": revised_output_str
        }

    def run_mock(self) -> Dict[str, Any]:
        """
        Executes a deterministic simulated boardroom run.
        """
        case_title = self.business_case.title
        is_finswarm = "lending" in case_title.lower() or "finswarm" in case_title.lower() or "finnova" in case_title.lower()
        is_saasswarm = "saas" in case_title.lower() or "cloudscale" in case_title.lower() or "arr" in case_title.lower()
        is_chipswarm = "chip" in case_title.lower() or "wafer" in case_title.lower() or "silicofoundry" in case_title.lower()

        # 1. ANALYSE STAGE
        research_out = (
            f"### 📊 Business & Market Research Intelligence Report\n\n"
            f"- **Target Sector:** {self.profile.industry}\n"
            f"- **Customer Demand Validation:** High market demand confirmed in core target segments.\n"
            f"- **Competitive Defensibility:** Physical assets / sticky enterprise integrations establish durable competitive moats.\n"
            f"- **Assumptions vs. Facts:** Key metrics verified against case brief; unverified extrapolations tagged [ASSUMPTION]."
        )
        self.trace_manager.record_event(
            stage=TraceStage.ANALYSE,
            agent_name="Business Research",
            agent_role="Business & Market Intelligence Analyst",
            task_name="Business & Market Dynamics Research",
            input_context="Active Business Case Brief",
            output=research_out
        )

        finance_out = (
            f"### 💰 Financial Feasibility & Unit Economics Report\n\n"
            f"- **Capital Budget Available:** {self.profile.available_capital}\n"
            f"- **Economics:** Evaluated candidate options under CapEx/OpEx, cash runway, and margins.\n"
            f"- **Hard Constraints Checked:** All financial budget caps and break-even timelines verified.\n"
            f"- **Recommendation:** Allocate capital toward highest risk-adjusted ROI while preserving minimum cash liquidity."
        )
        self.trace_manager.record_event(
            stage=TraceStage.ANALYSE,
            agent_name="Finance (CFO)",
            agent_role="Chief Financial Officer (CFO)",
            task_name="Financial Modeling & Capital Allocation",
            input_context="Research Intel + Financial Constraints",
            output=finance_out
        )

        marketing_out = (
            f"### 🎯 Commercial & Go-To-Market Strategy Report\n\n"
            f"- **Target Segmentation:** Direct key-account enterprise buyers and anchor customer partners.\n"
            f"- **Commercial Economics:** Positive LTV/CAC ratios with disciplined customer acquisition costs.\n"
            f"- **Sales Funnel:** Multi-stage enterprise conversion pipeline."
        )
        self.trace_manager.record_event(
            stage=TraceStage.ANALYSE,
            agent_name="Marketing (CMO)",
            agent_role="Chief Marketing & Commercial Officer (CMO)",
            task_name="Go-To-Market & Commercial Strategy",
            input_context="Research Intel + Case Brief",
            output=marketing_out
        )

        ops_out = (
            f"### ⚙️ Operational Feasibility & Delivery Report\n\n"
            f"- **Capacity Analysis:** {self.profile.resource_capacity}\n"
            f"- **Delivery Lead Times:** Critical path lead times identified; operational bottlenecks flagged for mitigation.\n"
            f"- **Team Readiness:** Internal engineering and operations capabilities aligned with rollout milestones."
        )
        self.trace_manager.record_event(
            stage=TraceStage.ANALYSE,
            agent_name="Operations",
            agent_role="Head of Global Operations & Infrastructure",
            task_name="Infrastructure & Execution Feasibility",
            input_context="Research findings + Supply chain constraints",
            output=ops_out
        )

        # 2. SHARE STAGE
        share_summary = (
            f"### 🔄 Boardroom Information Sharing & State Synchronization\n\n"
            f"Synchronized findings across Research, Finance, Marketing, and Operations:\n"
            f"1. **Research Intel:** Customer demand signals and competitive moat verified.\n"
            f"2. **Finance Model:** Evaluated capital allocation against budget caps and runway.\n"
            f"3. **Marketing Plan:** Target account acquisition plan and LTV/CAC models established.\n"
            f"4. **Operations Warning:** Delivery lead times and capacity constraints identified.\n\n"
            f"*Data synchronized and distributed to CRO and CEO.*"
        )
        self.trace_manager.record_share_event(
            shared_findings_summary=share_summary,
            recipient_agents=["Risk / Reviewer (CRO)", "CEO", "Finance (CFO)", "Marketing (CMO)", "Operations"]
        )

        # 3. CHALLENGE STAGE
        challenge_out = (
            f"### ⚡ Formal Adversarial Boardroom Challenge\n\n"
            f"- **Target Department Challenged:** **Finance (CFO)**\n"
            f"- **Challenged Recommendation / Assumption:** Aggressive upfront capital commitment without adequate liquidity reserve buffers.\n"
            f"- **Flaw Type:** Unsupported Financial Assumption & Solvency Vulnerability\n"
            f"- **Critique Evidence:** Unbudgeted execution lead times risk cash exhaustion before reaching positive operating cash flow.\n"
            f"- **Formal Demand:** Restructure capital allocation into phased tranches with clear milestone gates."
        )
        self.trace_manager.record_event(
            stage=TraceStage.CHALLENGE,
            agent_name="Risk / Reviewer (CRO)",
            agent_role="Chief Risk Officer & Adversarial Reviewer",
            task_name="Adversarial Challenge & Flaw Identification",
            input_context="All Department Reports from SHARE Stage",
            output=challenge_out
        )

        # 4. RESPONSE STAGE
        response_out = (
            f"### 🛡️ Department Response & Revised Recommendation\n\n"
            f"- **Responding Department:** **Finance (CFO)**\n"
            f"- **Verdict on Challenge:** **[ACCEPT & MODIFY]**\n"
            f"- **Defense & Rationale:** The CRO critique is accepted. Upfront capital exposure is restructured into a phased tranche deployment.\n"
            f"- **Revised Plan:** Commit initial capital to high-conviction priorities while preserving liquidity reserves to maintain >14 months runway."
        )
        self.trace_manager.record_event(
            stage=TraceStage.RESPONSE,
            agent_name="Finance (CFO)",
            agent_role="Chief Financial Officer",
            task_name="Department Response & Revision/Defense",
            input_context="CRO Adversarial Challenge",
            output=response_out
        )

        # 5. COMPARE STAGE
        matrix = StrategyEvaluator.evaluate_strategies(self.business_case, self.profile)
        compare_out = (
            f"### ⚖️ Boardroom Strategy Comparison Matrix (Baseline)\n\n"
            f"Evaluating candidate strategic alternatives:\n\n"
            f"| Dimension | Strategy Alpha (Primary Phased Focus) | Strategy Beta (Secondary Vector) |\n"
            f"|---|---|---|\n"
            f"| **Business Value & Moat** | High defensibility, verified customer demand, strong unit economics | Moderate defensibility, higher competitive friction |\n"
            f"| **Financial Viability** | Phased capital allocation; preserves liquidity buffer; achieves EBITDA break-even | Higher sales cycle drag; slower time to operating cash flow |\n"
            f"| **Operational Feasibility** | Aligns with existing team core competencies | Requires major new sales / infrastructure capability buildout |\n"
            f"| **Risk Profile** | Managed via phased tranche gates | High execution and market friction risks |\n\n"
            f"#### Comparative Synthesis for the CEO:\n"
            f"Strategy Alpha strongly outperforms on market validation, hard constraint satisfaction, and liquidity preservation."
        )
        self.trace_manager.record_event(
            stage=TraceStage.COMPARE,
            agent_name="Risk / Reviewer (CRO)",
            agent_role="Chief Risk Officer & Boardroom Reviewer",
            task_name="Strategy Comparison Matrix",
            input_context="Department Reports + Challenge + CFO Response",
            output=compare_out
        )

        # 6. DECIDE STAGE (13-Section QUORUM Executive Decision)
        if is_finswarm:
            decision_text = "Commit decisively to Strategy B (SME Embedded Factoring Credit Lines) while capping consumer microloans."
            scope_text = "SME B2B merchants with integrated escrow accounting platforms."
            calc_text = "Allocate $18.0M to SME credit (14.5% APR, 1.9% default); preserve $5.0M regulatory capital reserve; ROE projected at 16.8%."
            reject_text = "D2C Consumer Microloans rejected as primary vector due to 5.8% default rate breaching our 4.5% risk ceiling."
        elif is_saasswarm:
            decision_text = "Commit to Enterprise Dedicated VPC Expansion bundled with automated self-serve onboarding."
            scope_text = "Tier-1 enterprise accounts requiring single-tenant compliance (SOC2 Type II)."
            calc_text = "Allocate $5.2M investment; target 40 deals @ $250K ACV ($10.0M ARR addition); cloud hosting COGS capped at 22% (<25% cap)."
            reject_text = "Pure self-serve PLG rejected due to high developer churn (33%) and unmitigated hyperscaler price wars."
        elif is_chipswarm:
            decision_text = "Allocate Fab 7 capacity: Guarantee 8,000 WSPM for Automotive 28nm OEM commitments and allocate 12,000 WSPM to 5nm HPC AI chips."
            scope_text = "Tier-1 Automotive OEMs (28nm) + Hyperscaler AI hardware accelerators (5nm)."
            calc_text = "28nm (8k WSPM @ $3,200, 96% yield) + 5nm (12k WSPM @ $14,000, 68% yield) generates $118.4M monthly margin, covering $45M fixed costs."
            reject_text = "100% 5nm conversion rejected because defaulting on 8,000 WSPM automotive commitment triggers catastrophic $50M penalty."
        else:
            decision_text = "Commit decisively to Strategy Alpha with a Phased Tranche Deployment (4 Urban Fleet Charging Hubs)."
            scope_text = "Last-mile parcel delivery fleets in 4 Tier-1 logistics corridors (Dallas, Atlanta, Phoenix, Columbus)."
            calc_text = "4 Hubs @ $1.4M = $5.6M CapEx; preserves $9.4M cash buffer (20.8 mo runway); break-even achieved by Month 13."
            reject_text = "Standalone SaaS pivot rejected due to 60% adoption friction and 16+ month break-even timeline."

        baseline_ceo_out = (
            f"# QUORUM EXECUTIVE DECISION (BASELINE)\n\n"
            f"### 1. Selected Decision & Core Rationale\n"
            f"**{decision_text}**\n\n"
            f"### 2. Target / Scope & Evidence Used\n"
            f"- **Target Scope:** {scope_text}\n"
            f"- **Evidence Used:** Customer discovery sentiment confirms urgent demand; team technical capability matches delivery requirements.\n\n"
            f"### 3. Key Calculations\n"
            f"{calc_text}\n\n"
            f"### 4. Constraints Checked & How Challenge Reshaped Decision\n"
            f"- **How Challenge & Response Reshaped Plan:** The CRO challenge exposed solvency risks in unhedged upfront commitments; we restructured into milestone-gated tranches.\n"
            f"- **Budget / Capital Cap:** PASS (Allocated capital strictly within authorized limits).\n"
            f"- **Operating Break-Even / Loss Ceiling:** PASS (Satisfies all stated constraints).\n"
            f"- **Compliance & Regulatory Standards:** PASS (Full compliance roadmap integrated).\n\n"
            f"### 5. Approval / Operating Policy & Trade-offs Acknowledged\n"
            f"- **Tranche Gate Policy:** Release Phase 1 funding immediately. Follow-on allocations require achieving verified utilization and profitability benchmarks.\n"
            f"- **Trade-offs Acknowledged:** Focused capital allocation on core defensible moats rather than over-extending across multiple unproven vectors.\n\n"
            f"### 6. Pricing / Financial Plan\n"
            f"- **Financial Policy:** Sustainable unit economics with mandatory liquidity reserve preservation.\n\n"
            f"### 7. Key Risks & Mitigation Strategy (Risk Controls)\n"
            f"- **Execution Lead-Time Risk:** Mitigated by placing long-lead orders in Month 1 for pre-qualified sites/partners.\n"
            f"- **Demand / Utilization Risk:** Mitigated by requiring binding commercial agreements prior to major capital deployment.\n\n"
            f"### 8. Go-To-Market / Customer Plan\n"
            f"- Dedicated commercial key-account sales force targeting high-LTV anchor clients.\n\n"
            f"### 9. Phased Implementation Steps & Schedule\n"
            f"| Phase | Target Timeframe | Action Item | Responsible Department |\n"
            f"|---|---|---|---|\n"
            f"| **Phase 1** | Months 1–3 | Secure core contracts & initiate long-lead procurement | **Operations / Eng** |\n"
            f"| **Phase 2** | Months 2–5 | Sign binding anchor customer agreements | **Customer / Marketing** |\n"
            f"| **Phase 3** | Months 6–9 | Complete initial deployment & launch | **Operations & Engineering** |\n"
            f"| **Phase 4** | Months 10–13 | Scale capacity and achieve portfolio operating break-even | **Finance & Operations** |\n\n"
            f"### 10. Measurable Outcomes (Business KPIs)\n"
            f"1. **Operating Break-Even / Target Return:** Achieve operating break-even within 13 months.\n"
            f"2. **Contracted Capacity Utilization:** Secure ≥ 65% utilization by Month 9.\n"
            f"3. **Capital Preservation:** Maintain liquidity buffer above minimum required floors at all times.\n\n"
            f"### 11. Rejected Alternatives & Detailed Rationale\n"
            f"- **Rejected Alternative:** {reject_text}\n\n"
            f"### 12. Key Governing Assumptions\n"
            f"- Anchor customer volume commitments remain binding over the contract term.\n"
            f"- Macro cost and regulatory conditions remain within baseline tolerance.\n\n"
            f"### 13. Decision Confidence\n"
            f"**HIGH.** The strategy aligns with verified customer demand, satisfies all non-negotiable hard constraints, and preserves essential liquidity runway."
        )
        self.trace_manager.record_event(
            stage=TraceStage.DECIDE,
            agent_name="CEO",
            agent_role="Chief Executive Officer",
            task_name="QUORUM Executive Decision (Baseline)",
            input_context="All department reports, CRO Challenge, CFO Response, and Strategy Matrix",
            output=baseline_ceo_out
        )

        self.trace_manager.set_baseline_decision(baseline_ceo_out)
        trace_file = self.trace_manager.save_trace()

        return {
            "baseline_decision": baseline_ceo_out,
            "final_decision": baseline_ceo_out,
            "trace_file": str(trace_file),
            "trace_manager": self.trace_manager,
            "crew_output": baseline_ceo_out
        }

    def run_mock_surprise(self, surprise_event: Optional[SurpriseEvent] = None) -> Dict[str, Any]:
        """
        Executes a deterministic simulated Surprise Round adaptation on top of the baseline run.
        """
        surprise = surprise_event or DUMMY_SURPRISE_EVENT

        # 1. Run baseline first if not already run
        if not self.trace_manager.baseline_decision_raw:
            self.run_mock()

        # 2. Record SURPRISE stage
        self.trace_manager.record_surprise_event(surprise)

        # 3. Impact analysis
        impact = ImpactMapper.analyze_impact(surprise, self.business_case, self.profile)

        # 4. Re-run affected agents under REASSESS stage
        finance_rev_out = (
            f"### 🚨 Revised Financial Impact & Capital Allocation Report (Post-Surprise)\n\n"
            f"- **Surprise Event Ingested:** {surprise.id} ({surprise.type.value if hasattr(surprise.type, 'value') else str(surprise.type)})\n"
            f"- **Recalculated Financial Model:** Capital allocation adjusted to absorb shock.\n"
            f"- **Solvency Assessment:** Preserved cash buffer maintains required liquidity runway."
        )
        self.trace_manager.record_event(
            stage=TraceStage.REASSESS,
            agent_name="Finance (CFO)",
            agent_role="Chief Financial Officer",
            task_name="Surprise Financial Stress-Test & Budget Recalibration",
            input_context=f"Surprise Shock: {surprise.description}",
            output=finance_rev_out
        )

        ops_rev_out = (
            f"### 🚨 Revised Operational Delivery Plan (Post-Surprise)\n\n"
            f"- **Scope Adjustment:** Rescoped deployment batches and procurement lead times to eliminate bottlenecks.\n"
            f"- **Execution Timeline:** Concentrated field engineering on highest-conviction milestones."
        )
        self.trace_manager.record_event(
            stage=TraceStage.REASSESS,
            agent_name="Operations",
            agent_role="Head of Global Operations & Infrastructure",
            task_name="Surprise Rollout Rescoping & Lead-Time Safeguards",
            input_context=f"Surprise Shock: {surprise.description}",
            output=ops_rev_out
        )

        risk_rev_out = (
            f"### ⚖️ CRO Adversarial Reassessment & Strategy Matrix Update (Post-Surprise)\n\n"
            f"#### 1. Baseline Assumptions Invalidated\n"
            f"- ❌ *Invalidated:* {'; '.join(surprise.changed_assumptions)}\n\n"
            f"#### 2. Strategic Viability Re-evaluation\n"
            f"- Strategy Comparison Matrix updated under new constraints.\n"
            f"- Core strategy remains viable with calibrated scope, maintaining solvency safeguards."
        )
        self.trace_manager.record_event(
            stage=TraceStage.REASSESS,
            agent_name="Risk / Reviewer (CRO)",
            agent_role="Chief Risk Officer & Boardroom Reviewer",
            task_name="Surprise Risk Reassessment & Strategy Matrix Update",
            input_context="Surprise Financial and Operational Re-evaluations",
            output=risk_rev_out
        )

        # 5. DECIDE STAGE (Revised CEO Decision)
        revised_ceo_out = (
            f"# REVISED QUORUM EXECUTIVE DECISION (POST-SURPRISE)\n\n"
            f"## 🚨 Executive Surprise Adaptation Summary\n\n"
            f"### What Changed\n"
            f"{surprise.description}\n\n"
            f"### Invalidated Previous Assumptions\n"
            f"- {chr(10).join('- ' + a for a in surprise.changed_assumptions)}\n\n"
            f"### Materially Affected Agents Rerun\n"
            f"- **Rerun Specialists:** {', '.join(impact['materially_affected_agents'])}\n"
            f"- **Preserved Findings:** Unaffected research and core commercial positioning preserved.\n\n"
            f"### Strategic Viability Assessment\n"
            f"The core strategic thesis remains robust, but the execution scope is recalibrated to satisfy new constraints.\n\n"
            f"### Why the Decision Remained Stable vs. Changed\n"
            f"- **Remained Stable:** Did not pivot to infeasible alternatives.\n"
            f"- **Changed:** Rescoped upfront capital and milestones to safeguard liquidity.\n\n"
            f"---\n\n"
            f"## 🏛️ Revised Executive Mandate (13-Section QUORUM Format)\n\n"
            f"### 1. Selected Revised Decision & Core Rationale\n"
            f"**Commit to a Recalibrated Tranche Deployment adapted to the new operating constraint.**\n"
            f"The company adapts capital allocation and delivery scope to maintain solvency through break-even.\n\n"
            f"### 2. Target / Scope\n"
            f"- Focus resources exclusively on pre-cleared, high-conviction target customer cohorts.\n\n"
            f"### 3. Key Calculations\n"
            f"- Adjusted capital plan secures at least 14.0 months of runway and meets revised budget constraints.\n\n"
            f"### 4. Constraints Checked\n"
            f"- **Updated Budget / Risk Cap:** PASS (Complies with shock constraints).\n"
            f"- **Break-Even Timeline:** PASS (Maintained within non-negotiable deadline).\n\n"
            f"### 5. Approval / Operating Policy\n"
            f"- Tranche Gate 1 authorized immediately; follow-on funding strictly gated on milestone achievement.\n\n"
            f"### 6. Pricing / Financial Plan\n"
            f"- Unit economics adjusted with mandatory minimum liquidity reserve floor.\n\n"
            f"### 7. New Risks & Mitigation Strategy (Risk Controls)\n"
            f"- **Shock Mitigation:** Contractual minimums and phased vendor commitments lock in pricing.\n\n"
            f"### 8. Go-To-Market / Customer Plan\n"
            f"- Concentrate sales efforts on priority high-conversion anchor accounts.\n\n"
            f"### 9. Updated Phased Implementation Steps\n"
            f"| Phase | Target Timeframe | Action Item | Responsible Department |\n"
            f"|---|---|---|---|\n"
            f"| **Phase 1** | Months 1–2 | Recalibrate procurement batches & secure anchor commitments | **Operations & Sales** |\n"
            f"| **Phase 2** | Months 3–6 | Commission priority rollout units | **Operations & Eng** |\n"
            f"| **Phase 3** | Months 7–10 | Scale capacity to break-even threshold | **Finance & Operations** |\n\n"
            f"### 10. Updated Measurable Business KPIs\n"
            f"1. **EBITDA Neutrality:** Reach operating break-even within 12–13 months.\n"
            f"2. **Contracted Capacity Target:** Secure ≥ 70% utilization by Month 8.\n"
            f"3. **Strict Liquidity Floor:** Maintain required liquidity reserves at all times.\n\n"
            f"### 11. Rejected Alternatives\n"
            f"- Unviable pivot options rejected due to prolonged lead times and excessive burn in capital-constrained environments.\n\n"
            f"### 12. New Governing Assumptions\n"
            f"- Monthly cash burn will remain capped under revised budget levels.\n"
            f"- Supplier lead times and customer commitments will adhere to updated milestones.\n\n"
            f"### 13. Decision Confidence\n"
            f"**HIGH.** The strategy actively adapts to the surprise shock, complies with all constraints, and protects enterprise liquidity."
        )
        self.trace_manager.record_event(
            stage=TraceStage.DECIDE,
            agent_name="CEO",
            agent_role="Chief Executive Officer",
            task_name="Revised QUORUM Executive Decision (Post-Surprise)",
            input_context=f"Surprise Shock: {surprise.description} + Reassessed Reports",
            output=revised_ceo_out
        )

        self.trace_manager.set_revised_decision(revised_ceo_out)
        trace_file = self.trace_manager.save_trace()

        return {
            "baseline_decision": self.trace_manager.baseline_decision_raw,
            "revised_decision": revised_ceo_out,
            "surprise_event": surprise,
            "trace_file": str(trace_file),
            "trace_manager": self.trace_manager,
            "crew_output": revised_ceo_out
        }


def run_boardroom_swarm(
    business_case: BusinessCase,
    llm: Optional[LLM] = None,
    surprise_event: Optional[SurpriseEvent] = None
) -> Dict[str, Any]:
    crew_orchestrator = BoardroomCrew(business_case=business_case, llm=llm)
    baseline_result = crew_orchestrator.run()
    if surprise_event:
        return crew_orchestrator.adapt_to_surprise(surprise_event=surprise_event)
    return baseline_result
