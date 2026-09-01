"""
Comprehensive Test Suite for Domain-Adaptive Quorum Swarm Architecture.

Tests cover:
1. FINSWARM baseline (Fintech Credit/Treasury mapping)
2. FINSWARM surprise (Credit loss spike)
3. SAASSWARM baseline (Enterprise Cloud SaaS)
4. SAASSWARM surprise (Competitor price war / churn)
5. CHIPSWARM baseline (Semiconductor Fab 7 capacity)
6. CHIPSWARM surprise (EUV tool outage)
7. Unseen synthetic business case (Space Logistics / Biotechnology)
8. Unseen surprise type adaptation
9. Numerical constraint violation & infeasibility flagging
10. Dynamic agent selection ceiling (Strictly <= 8 agents)
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


from backend.models.business_case import (
    BusinessCase,
    SurpriseEvent,
    SurpriseType,
    FINSWARM_CASE,
    FINSWARM_SURPRISE,
    SAASSWARM_CASE,
    SAASSWARM_SURPRISE,
    CHIPSWARM_CASE,
    CHIPSWARM_SURPRISE,
    DUMMY_BUSINESS_CASE,
    DUMMY_SURPRISE_EVENT,
)
from backend.case.case_parser import CaseParser
from backend.case.case_profiler import CaseProfiler
from backend.case.domain_mapper import DomainMapper
from backend.engine.calculator import CalculationEngine
from backend.engine.constraint_validator import ConstraintValidator
from backend.engine.strategy_evaluator import StrategyEvaluator
from backend.surprise.surprise_analyzer import SurpriseAnalyzer
from backend.surprise.impact_mapper import ImpactMapper
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.trace.trace_manager import TraceStage


def test_1_finswarm_baseline():
    """Test 1: FINSWARM baseline execution maps Credit/Treasury and produces 13-section decision."""
    orchestrator = BoardroomCrew(business_case=FINSWARM_CASE)
    res = orchestrator.run_mock()
    dec = res["baseline_decision"]
    assert "QUORUM EXECUTIVE DECISION" in dec
    assert "1. Selected Decision" in dec
    assert "SME Embedded" in dec or "Factoring" in dec
    assert "13. Decision Confidence" in dec
    print("[PASS] Test 1: FINSWARM baseline adapts and produces valid executive decision.")


def test_2_finswarm_surprise():
    """Test 2: FINSWARM surprise (credit loss spike) triggers impact analysis and revised decision."""
    orchestrator = BoardroomCrew(business_case=FINSWARM_CASE)
    res = orchestrator.run_mock_surprise(FINSWARM_SURPRISE)
    rev = res["revised_decision"]
    assert "REVISED QUORUM EXECUTIVE DECISION" in rev
    assert "Invalidated Previous Assumptions" in rev
    assert "13. Decision Confidence" in rev
    assert res["baseline_decision"] != ""
    print("[PASS] Test 2: FINSWARM surprise adapts and preserves baseline decision.")


def test_3_saasswarm_baseline():
    """Test 3: SAASSWARM baseline adapts to cloud software economics."""
    orchestrator = BoardroomCrew(business_case=SAASSWARM_CASE)
    res = orchestrator.run_mock()
    dec = res["baseline_decision"]
    assert "QUORUM EXECUTIVE DECISION" in dec
    assert "Enterprise Dedicated VPC" in dec or "ARR" in dec
    assert "13. Decision Confidence" in dec
    print("[PASS] Test 3: SAASSWARM baseline adapts to enterprise cloud economics.")


def test_4_saasswarm_surprise():
    """Test 4: SAASSWARM surprise (competitor price cut) adapts strategy."""
    orchestrator = BoardroomCrew(business_case=SAASSWARM_CASE)
    res = orchestrator.run_mock_surprise(SAASSWARM_SURPRISE)
    rev = res["revised_decision"]
    assert "REVISED QUORUM EXECUTIVE DECISION" in rev
    assert "What Changed" in rev
    print("[PASS] Test 4: SAASSWARM surprise round adapts successfully.")


def test_5_chipswarm_baseline():
    """Test 5: CHIPSWARM baseline adapts to cleanroom wafer capacity and yield economics."""
    orchestrator = BoardroomCrew(business_case=CHIPSWARM_CASE)
    res = orchestrator.run_mock()
    dec = res["baseline_decision"]
    assert "QUORUM EXECUTIVE DECISION" in dec
    assert "28nm" in dec and "5nm" in dec
    assert "13. Decision Confidence" in dec
    print("[PASS] Test 5: CHIPSWARM baseline optimizes foundry line allocation.")


def test_6_chipswarm_surprise():
    """Test 6: CHIPSWARM surprise (EUV tool outage) adapts throughput."""
    orchestrator = BoardroomCrew(business_case=CHIPSWARM_CASE)
    res = orchestrator.run_mock_surprise(CHIPSWARM_SURPRISE)
    rev = res["revised_decision"]
    assert "REVISED QUORUM EXECUTIVE DECISION" in rev
    assert "Invalidated Previous Assumptions" in rev
    print("[PASS] Test 6: CHIPSWARM surprise adapts to tool capacity disruption.")


def test_7_unseen_synthetic_case():
    """Test 7: Unseen synthetic business case (AeroOrbit Space Logistics)."""
    synthetic_case = BusinessCase(
        title="[SYNTHETIC] AeroOrbit: LEO Heavy Rideshare vs Dedicated Orbital Tug",
        problem="AeroOrbit has $30M capital to commercialize in-space transportation. SmallSat constellation operators require precise orbital plane insertion.",
        objective="Achieve EBITDA break-even within 15 months while maintaining 99.5% mission launch reliability.",
        context="AeroOrbit operates autonomous space tug stages for satellite repositioning.",
        constraints=[
            "Total capital expenditure capped at $30.0M.",
            "Must achieve EBITDA break-even within 15 months.",
            "FAA and FCC commercial spaceflight licensing requires 6 months lead time."
        ],
        available_data={
            "launch_economics": {
                "tug_unit_cost": "$4.2M",
                "charter_price": "$9.5M / mission",
                "cash_burn": "$600K/month"
            }
        },
        assumptions=["Rocket Lab and SpaceX rideshare availability remains predictable."],
        mandatory_roles=["Mission Research", "Finance and Treasury", "Risk Reviewer", "Propulsion Operations", "CEO"]
    )
    profile = CaseProfiler.profile(synthetic_case)
    assert profile.company != "UNKNOWN"
    assert "Space" in profile.industry or "Aerospace" in profile.industry

    orchestrator = BoardroomCrew(business_case=synthetic_case)
    res = orchestrator.run_mock()
    assert "QUORUM EXECUTIVE DECISION" in res["baseline_decision"]
    print("[PASS] Test 7: Unseen synthetic business case profiled and solved.")


def test_8_unseen_surprise_type():
    """Test 8: Unseen surprise type adaptation (regulatory export embargo shock)."""
    unseen_surprise = SurpriseEvent(
        id="SURPRISE-UNSEEN-EMBARGO-001",
        type=SurpriseType.REGULATORY_CHANGE,
        description="Government issues immediate export ban on dual-use optical thrusters, halting international customer contracts.",
        severity="CRITICAL",
        affected_departments=["Compliance & Quality", "Customer & Marketing", "Finance & Economics"],
        changed_assumptions=["International export revenue stream is halted."]
    )
    impact = ImpactMapper.analyze_impact(unseen_surprise, DUMMY_BUSINESS_CASE, CaseProfiler.profile(DUMMY_BUSINESS_CASE))
    assert "Compliance / Quality" in impact["materially_affected_agents"]
    assert len(impact["invalidated_assumptions"]) >= 1

    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    res = orchestrator.run_mock_surprise(unseen_surprise)
    assert "REVISED QUORUM EXECUTIVE DECISION" in res["revised_decision"]
    print("[PASS] Test 8: Unseen surprise type analyzed and adapted.")


def test_9_numerical_constraint_violation_flagged():
    """Test 9: Numerical constraint violation is caught by Calculation & Constraint engine."""
    math_res = CalculationEngine.evaluate_strategy_math(
        strategy_name="Unconstrained Overspend Strategy",
        strategy_data={"investment_required": "$35.0M"},  # Exceeds $15M budget
        case=DUMMY_BUSINESS_CASE
    )
    profile = CaseProfiler.profile(DUMMY_BUSINESS_CASE)
    is_feasible, evaluations, reasons = ConstraintValidator.validate_strategy(
        strategy_name="Unconstrained Overspend Strategy",
        math_result=math_res,
        case=DUMMY_BUSINESS_CASE,
        profile=profile
    )
    assert is_feasible is False
    assert len(reasons) >= 1
    assert "exceeds hard budget cap" in reasons[0]
    print("[PASS] Test 9: Deterministic engine flags constraint violation as INFEASIBLE.")


def test_10_agent_limit_ceiling():
    """Test 10: Dynamic agent selection strictly enforces <= 8 agents across all domains."""
    cases_to_test = [DUMMY_BUSINESS_CASE, FINSWARM_CASE, SAASSWARM_CASE, CHIPSWARM_CASE]
    for c in cases_to_test:
        crew_orch = BoardroomCrew(business_case=c)
        agents = crew_orch.assemble_active_agents()
        assert len(agents) <= 8, f"Agent count {len(agents)} exceeded maximum 8 for {c.title}"
        assert len(agents) >= 4, f"Agent count {len(agents)} below minimum 4 for {c.title}"
    print("[PASS] Test 10: Agent limit ceiling verified: strictly between 4 and 8 active agents across all domains.")


def run_all():
    print("=================================================================")
    print("Running Domain-Adaptive Quorum Multi-Agent Swarm Test Suite...")
    print("=================================================================")
    test_1_finswarm_baseline()
    test_2_finswarm_surprise()
    test_3_saasswarm_baseline()
    test_4_saasswarm_surprise()
    test_5_chipswarm_baseline()
    test_6_chipswarm_surprise()
    test_7_unseen_synthetic_case()
    test_8_unseen_surprise_type()
    test_9_numerical_constraint_violation_flagged()
    test_10_agent_limit_ceiling()
    print("=================================================================")
    print("✅ ALL 10 DOMAIN-ADAPTIVE QUORUM TESTS PASSED SUCCESSFULLY!")
    print("=================================================================")


if __name__ == "__main__":
    run_all()
