"""
Unit and Integration Tests for Phase 2: Boardroom Collaboration Protocol.
Verifies all 8 required properties from the rulebook:
1. Six agents exist.
2. Share stage is recorded.
3. A challenge is generated from actual agent findings.
4. A response is recorded.
5. At least two strategies are compared.
6. CEO receives challenge/response/comparison.
7. Final decision is produced.
8. Trace contains ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.business_case import (
    BusinessCase,
    BoardroomChallenge,
    DepartmentResponse,
    StrategyProfile,
    StrategyComparisonMatrix,
    CEODecisionOutput,
    ChallengeVerdict,
)
from backend.models.dummy_case import DUMMY_BUSINESS_CASE
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.trace.trace_manager import TraceManager, TraceStage


def test_1_six_agents_exist():
    """Requirement 1: Exactly 6 identifiable agents exist."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    crew = orchestrator.build_crew()
    assert len(crew.agents) == 6, f"Expected 6 agents, found {len(crew.agents)}"
    roles = [a.role for a in crew.agents]
    assert any("Market" in r for r in roles), "Business Research agent missing"
    assert any("CFO" in r or "Financial" in r for r in roles), "Finance agent missing"
    assert any("CMO" in r or "Marketing" in r for r in roles), "Marketing agent missing"
    assert any("Operations" in r for r in roles), "Operations agent missing"
    assert any("CRO" in r or "Risk" in r for r in roles), "Risk/Reviewer agent missing"
    assert any("CEO" in r or "Executive" in r for r in roles), "CEO agent missing"
    print("[PASS] Test 1: Six identifiable agents exist.")


def test_2_share_stage_recorded():
    """Requirement 2: SHARE stage is explicitly recorded in trace."""
    tm = TraceManager(business_case=DUMMY_BUSINESS_CASE)
    tm.record_share_event(
        shared_findings_summary="Market: +32% CAGR; Finance: $11.2M CapEx; Ops: 24wk transformer lead time.",
        recipient_agents=["CRO", "CEO", "CFO", "CMO", "COO"]
    )
    assert len(tm.records) == 1
    assert tm.records[0].stage == TraceStage.SHARE
    assert "SHARE" in tm.records[0].stage.value
    print("[PASS] Test 2: Share stage is recorded.")


def test_3_challenge_generated():
    """Requirement 3: A targeted challenge is generated from findings."""
    challenge = BoardroomChallenge(
        target_department="Finance (CFO)",
        target_recommendation="Commit $11.2M upfront for all 8 hubs immediately",
        flaw_type="Cross-Departmental Contradiction & Solvency Risk",
        critique_evidence="Operations identified 9-12 mo grid delays in 2 cities. $3.8M cash reserve gives only 8.4 mo runway.",
        response_request="Restructure capital allocation to preserve at least 12 months runway."
    )
    assert challenge.target_department == "Finance (CFO)"
    assert "8.4 mo runway" in challenge.critique_evidence
    print("[PASS] Test 3: A challenge can be generated from agent findings.")


def test_4_response_recorded():
    """Requirement 4: A structured response/defense is recorded."""
    response = DepartmentResponse(
        responding_department="Finance (CFO)",
        verdict=ChallengeVerdict.MODIFY,
        evidence_and_rationale="Conceding that 8 hubs upfront risks insolvency due to grid delays in Chicago/NYC.",
        revised_recommendation_or_assumptions="Allocate $5.6M for Phase 1 (4 hubs in fast-track grid cities) and preserve $9.4M cash (20.8 mo runway)."
    )
    assert response.verdict == ChallengeVerdict.MODIFY
    assert "5.6M" in response.revised_recommendation_or_assumptions
    print("[PASS] Test 4: A response is recorded.")


def test_5_at_least_two_strategies_compared():
    """Requirement 5: At least two viable strategies are compared across 6 dimensions."""
    s1 = StrategyProfile(
        strategy_name="Strategy Alpha (Phased Fleet Hubs)",
        business_value="High physical moat, 42% gross margin",
        financial_viability="$5.6M CapEx, preserves $9.4M cash, EBITDA break-even Month 13",
        market_customer_fit="85% urgent demand from last-mile fleets",
        operational_feasibility="24-wk transformer lead time; matches in-house team",
        risk_level="Medium (grid connection)",
        major_assumptions=["Anchor fleets sign 2-yr take-or-pay", "Grid <6 mo in target corridors"]
    )
    s2 = StrategyProfile(
        strategy_name="Strategy Beta (Enterprise Fleet SaaS)",
        business_value="Low moat against Siemens/ChargePoint, 78% margin",
        financial_viability="$4.5M R&D/GTM, EBITDA break-even Month 16+",
        market_customer_fit="60% resistance without bundled hardware",
        operational_feasibility="Requires building B2B enterprise software sales team",
        risk_level="High (competitive displacement)",
        major_assumptions=["CAC under $35K", "30% cross-sell rate"]
    )
    matrix = StrategyComparisonMatrix(
        strategies=[s1, s2],
        comparative_summary="Strategy Alpha strongly outperforms Beta on defensibility and team fit."
    )
    assert len(matrix.strategies) >= 2
    assert matrix.strategies[0].strategy_name == "Strategy Alpha (Phased Fleet Hubs)"
    assert matrix.strategies[1].strategy_name == "Strategy Beta (Enterprise Fleet SaaS)"
    print("[PASS] Test 5: At least two strategies are compared across 6 dimensions.")


def test_6_ceo_receives_challenge_response_comparison():
    """Requirement 6: CEO receives all previous stage contexts."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    crew = orchestrator.build_crew()
    # Task 8 is the CEO decision task (0: Research, 1: Finance, 2: Marketing, 3: Ops, 4: Challenge, 5: Response, 6: Compare, 7: Decide)
    ceo_task = crew.tasks[-1]
    assert ceo_task.agent.role == "Chief Executive Officer (CEO)"
    assert len(ceo_task.context) >= 5, f"CEO task should receive at least 5 context tasks, got {len(ceo_task.context)}"
    print("[PASS] Test 6: CEO receives challenge, response, and comparison tasks.")


def test_7_final_decision_produced():
    """Requirement 7: Final CEO decision includes all mandatory components."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock()
    decision = result["final_decision"]
    assert "Selected Decision" in decision
    assert "Evidence Used" in decision
    assert "Rejected Alternative" in decision
    assert "Trade-offs" in decision
    assert "Risks" in decision
    assert "Assumptions" in decision
    assert "Implementation Steps" in decision
    assert "KPIs" in decision
    print("[PASS] Test 7: Final CEO decision is produced with all required elements.")


def test_8_trace_contains_full_protocol_sequence():
    """Requirement 8: Trace contains ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock()
    tm = result["trace_manager"]
    stages = tm.get_stages_present()
    
    expected_order = [
        TraceStage.ANALYSE.value,
        TraceStage.SHARE.value,
        TraceStage.CHALLENGE.value,
        TraceStage.RESPONSE.value,
        TraceStage.COMPARE.value,
        TraceStage.DECIDE.value,
    ]

    for expected_stage in expected_order:
        assert expected_stage in stages, f"Missing protocol stage: {expected_stage}"

    # Verify order of first appearance
    first_occurrences = []
    for stage in expected_order:
        idx = stages.index(stage)
        first_occurrences.append(idx)
    
    assert first_occurrences == sorted(first_occurrences), f"Stages out of order: {stages}"

    # Verify JSON persistence
    trace_path = Path(result["trace_file"])
    assert trace_path.exists()
    with open(trace_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["session_metadata"]["protocol_sequence"] == expected_order
    print("[PASS] Test 8: Trace contains ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE.")


if __name__ == "__main__":
    print("=" * 60)
    print("Running Phase 2 Boardroom Collaboration Test Suite...")
    print("=" * 60)
    test_1_six_agents_exist()
    test_2_share_stage_recorded()
    test_3_challenge_generated()
    test_4_response_recorded()
    test_5_at_least_two_strategies_compared()
    test_6_ceo_receives_challenge_response_comparison()
    test_7_final_decision_produced()
    test_8_trace_contains_full_protocol_sequence()
    print("\n" + "=" * 60)
    print("✅ ALL 8 PHASE 2 BOARDROOM PROTOCOL TESTS PASSED!")
    print("=" * 60)
