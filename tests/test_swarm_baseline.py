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

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.business_case import BusinessCase, CEODecisionOutput
from backend.models.dummy_case import DUMMY_BUSINESS_CASE
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.trace.trace_manager import TraceManager, TraceStage


def test_business_case_model():
    """Verify BusinessCase serialization and markdown brief generation."""
    case = DUMMY_BUSINESS_CASE
    assert case.title is not None
    assert len(case.constraints) == 4
    assert "financial_metrics" in case.available_data
    brief = case.to_brief_markdown()
    assert "# BUSINESS CASE BRIEF:" in brief
    assert "## 1. Problem Statement" in brief
    assert "## 4. Key Constraints" in brief
    assert "## 5. Available Quantitative & Operational Data" in brief


def test_crew_architecture_assembly():
    """Verify all 6 agents and linked tasks are properly assembled."""
    orchestrator = BoardroomCrew(business_case=DUMMY_BUSINESS_CASE)
    crew = orchestrator.build_crew()

    assert len(crew.agents) == 6
    roles = [a.role for a in crew.agents]
    assert any("Market" in r for r in roles)
    assert any("CFO" in r or "Financial" in r for r in roles)
    assert any("CMO" in r or "Marketing" in r for r in roles)
    assert any("Operations" in r for r in roles)
    assert any("CRO" in r or "Risk" in r for r in roles)
    assert any("CEO" in r or "Executive" in r for r in roles)

    # Crew tasks include the 6 collaboration protocol tasks
    assert len(crew.tasks) == 8
    # Task 4 is challenge (receives 4 depts), Task 5 is response, Task 6 is compare, Task 7 is CEO (receives all prior tasks)
    assert len(crew.tasks[4].context) == 4
    assert len(crew.tasks[7].context) >= 5


def test_trace_manager_persistence(tmp_path):
    """Verify TraceManager records outputs and saves valid JSON."""
    tm = TraceManager(business_case=DUMMY_BUSINESS_CASE)
    tm.record_event(
        stage=TraceStage.ANALYSE,
        agent_name="Business Research",
        agent_role="Chief Market Intelligence Analyst",
        task_name="Market Analysis",
        input_context="Test input context",
        output="Market analysis complete with verified data."
    )
    tm.record_share_event(
        shared_findings_summary="Shared state data",
        recipient_agents=["CRO", "CEO"]
    )
    tm.record_event(
        stage=TraceStage.CHALLENGE,
        agent_name="Risk Reviewer",
        agent_role="Chief Risk Officer",
        task_name="Risk Assessment",
        input_context="Test review context",
        output="Identified 2 unverified assumptions."
    )
    tm.set_final_decision("Test final CEO decision.")
    
    saved_path = tm.save_trace()
    assert Path(saved_path).exists()

    with open(saved_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert data["session_metadata"]["system"] == "Quorum — The AI Boardroom"
    assert len(data["agent_execution_trace"]) == 3
    assert data["final_decision"] == "Test final CEO decision."


if __name__ == "__main__":
    print("Running Quorum Phase 1 & 2 Baseline Unit Tests...")
    test_business_case_model()
    print("[PASS] test_business_case_model passed")
    test_crew_architecture_assembly()
    print("[PASS] test_crew_architecture_assembly passed")
    test_trace_manager_persistence(Path("backend/trace/runs"))
    print("[PASS] test_trace_manager_persistence passed")
    print("\n[SUCCESS] All baseline unit tests passed successfully!")
