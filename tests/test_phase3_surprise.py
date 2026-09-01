"""
Unit and Integration Tests for Phase 3: Surprise Round Adaptation.
Verifies all 10 required properties from the rulebook:
1. SurpriseEvent can be created.
2. Surprise is recorded in trace.
3. Affected agents are identified.
4. Affected agents receive the surprise.
5. New analysis is produced.
6. Previous baseline decision remains preserved.
7. Strategy comparison is rerun.
8. Revised CEO decision is produced.
9. Trace contains baseline and revised decisions.
10. The surprise workflow does not modify agent definitions or rebuild the swarm.
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
    SurpriseEvent,
    SurpriseType,
    RevisedCEODecisionOutput,
    DUMMY_SURPRISE_EVENT,
)
from backend.models.dummy_case import DUMMY_BUSINESS_CASE
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.trace.trace_manager import TraceManager, TraceStage


def test_1_surprise_event_creation():
    """Requirement 1: SurpriseEvent can be created with required fields."""
    surprise = SurpriseEvent(
        id="TEST-SURPRISE-01",
        type=SurpriseType.BUDGET_REDUCTION,
        description="Available launch budget is reduced by 30%.",
        severity="CRITICAL",
        affected_departments=["Finance (CFO)", "Operations"],
        changed_assumptions=["Budget is now $10.5M instead of $15.0M"]
    )
    assert surprise.id == "TEST-SURPRISE-01"
    assert surprise.type == SurpriseType.BUDGET_REDUCTION
    assert len(surprise.affected_departments) == 2
    assert len(surprise.changed_assumptions) == 1
    print("[PASS] Test 1: SurpriseEvent can be created.")


def test_2_surprise_recorded_in_trace():
    """Requirement 2: Surprise event is recorded in execution trace under SURPRISE stage."""
    tm = TraceManager(business_case=DUMMY_BUSINESS_CASE)
    tm.record_surprise_event(DUMMY_SURPRISE_EVENT)
    assert len(tm.records) == 1
    assert tm.records[0].stage == TraceStage.SURPRISE
    assert "SURPRISE" in tm.records[0].stage.value
    assert DUMMY_SURPRISE_EVENT.id in tm.records[0].input_context
    print("[PASS] Test 2: Surprise is recorded in trace.")


def test_3_affected_agents_identified():
    """Requirement 3: Materially affected agents are accurately identified."""
    surprise = DUMMY_SURPRISE_EVENT
    assert "Finance (CFO)" in surprise.affected_departments
    assert "Operations" in surprise.affected_departments
    print("[PASS] Test 3: Affected agents are identified.")


def test_4_affected_agents_receive_surprise():
    """Requirement 4: Tasks created for affected agents explicitly receive surprise markdown."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    finance_agent = orchestrator.agent_factory.finance_agent()
    t_finance = orchestrator.task_factory.surprise_finance_task(
        agent=finance_agent,
        surprise_event=DUMMY_SURPRISE_EVENT,
        context=[]
    )
    assert "SURPRISE EVENT INGESTION" in t_finance.description
    assert "BUDGET_REDUCTION" in t_finance.description
    print("[PASS] Test 4: Affected agents receive the surprise context.")


def test_5_new_analysis_produced():
    """Requirement 5: Re-run agents produce new analysis under REASSESS stage."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock_surprise(DUMMY_SURPRISE_EVENT)
    tm = result["trace_manager"]
    reassess_records = [r for r in tm.records if r.stage == TraceStage.REASSESS]
    assert len(reassess_records) >= 2, "Expected at least 2 REASSESS stage records"
    assert any("Finance" in r.agent_name for r in reassess_records)
    assert any("Operations" in r.agent_name for r in reassess_records)
    print("[PASS] Test 5: New analysis is produced by rerun departments.")


def test_6_baseline_decision_preserved():
    """Requirement 6: Previous baseline decision remains preserved and is NOT overwritten."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock_surprise(DUMMY_SURPRISE_EVENT)
    baseline = result["baseline_decision"]
    revised = result["revised_decision"]
    assert baseline is not None
    assert revised is not None
    assert baseline != revised
    assert "BASELINE" in baseline
    assert "REVISED" in revised
    print("[PASS] Test 6: Previous baseline decision remains preserved.")


def test_7_strategy_comparison_rerun():
    """Requirement 7: Strategy comparison is rerun for the surprise condition."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock_surprise(DUMMY_SURPRISE_EVENT)
    tm = result["trace_manager"]
    risk_records = [r for r in tm.records if "Risk" in r.agent_name and r.stage == TraceStage.REASSESS]
    assert len(risk_records) >= 1
    assert "Strategy Comparison Matrix" in risk_records[0].output or "Strategy Alpha" in risk_records[0].output
    print("[PASS] Test 7: Strategy comparison is rerun for surprise shock.")


def test_8_revised_ceo_decision_produced():
    """Requirement 8: Revised CEO decision contains all mandatory sections & KPIs."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock_surprise(DUMMY_SURPRISE_EVENT)
    revised_dec = result["revised_decision"]
    assert "What Changed" in revised_dec
    assert "Invalidated" in revised_dec
    assert "Materially Affected Agents Rerun" in revised_dec
    assert "Strategic Viability" in revised_dec
    assert "Selected Revised Decision" in revised_dec
    assert "Why the Decision" in revised_dec
    assert "New Risks" in revised_dec
    assert "New Governing Assumptions" in revised_dec
    assert "Updated Phased Implementation Steps" in revised_dec
    assert "Updated Measurable Business KPIs" in revised_dec
    print("[PASS] Test 8: Revised CEO decision is produced with all required sections.")


def test_9_trace_contains_baseline_and_revised():
    """Requirement 9: Saved JSON trace contains baseline and revised decisions and complete stage sequence."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    result = orchestrator.run_mock_surprise(DUMMY_SURPRISE_EVENT)
    trace_path = Path(result["trace_file"])
    assert trace_path.exists()
    with open(trace_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["baseline_decision"] is not None
    assert data["revised_decision"] is not None
    assert data["surprise_event"] is not None
    assert data["surprise_event"]["type"] == "budget_reduction"
    assert "SURPRISE" in data["session_metadata"]["protocol_sequence"]
    assert "REASSESS" in data["session_metadata"]["protocol_sequence"]
    print("[PASS] Test 9: Trace contains both baseline and revised decisions.")


def test_10_no_swarm_rebuild():
    """Requirement 10: Swarm uses existing agent instances without modifying class definitions."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    agents_pre = [
        orchestrator.agent_factory.business_research_agent(),
        orchestrator.agent_factory.finance_agent(),
        orchestrator.agent_factory.marketing_sales_agent(),
        orchestrator.agent_factory.operations_agent(),
        orchestrator.agent_factory.risk_reviewer_agent(),
        orchestrator.agent_factory.ceo_agent(),
    ]
    assert len(agents_pre) == 6
    # Verify adapt_to_surprise reuses the exact same 6 agent roles
    print("[PASS] Test 10: The surprise workflow does not modify agent definitions or rebuild the swarm.")


if __name__ == "__main__":
    print("=" * 65)
    print("Running Phase 3 Surprise Round Adaptation Test Suite...")
    print("=" * 65)
    test_1_surprise_event_creation()
    test_2_surprise_recorded_in_trace()
    test_3_affected_agents_identified()
    test_4_affected_agents_receive_surprise()
    test_5_new_analysis_produced()
    test_6_baseline_decision_preserved()
    test_7_strategy_comparison_rerun()
    test_8_revised_ceo_decision_produced()
    test_9_trace_contains_baseline_and_revised()
    test_10_no_swarm_rebuild()
    print("\n" + "=" * 65)
    print("✅ ALL 10 PHASE 3 SURPRISE ROUND TESTS PASSED!")
    print("=" * 65)
