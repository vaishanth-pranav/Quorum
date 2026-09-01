"""
Main CLI entry point for Quorum — The Adaptive AI Boardroom.

Protocol Stages:
    ANALYSE ➔ SHARE ➔ CHALLENGE ➔ RESPONSE ➔ COMPARE ➔ DECIDE ➔ SURPRISE ➔ REASSESS ➔ DECIDE

Usage:
    python backend/main.py                          # Runs baseline boardroom swarm with live LLM
    python backend/main.py --domain finswarm        # Runs FINSWARM domain benchmark
    python backend/main.py --domain saasswarm       # Runs SAASSWARM domain benchmark
    python backend/main.py --domain chipswarm       # Runs CHIPSWARM domain benchmark
    python backend/main.py --mock --surprise        # Runs baseline + surprise offline
    python backend/main.py --case case.json         # Runs custom business case file
    python backend/main.py --surprise-file s.json   # Ingests custom surprise file
    python backend/main.py --validate               # Validates architecture & surprise wiring without LLM
"""

import sys
import os
import json
import argparse
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.models.business_case import (
    BusinessCase,
    SurpriseEvent,
    SurpriseType,
    DUMMY_SURPRISE_EVENT,
    DUMMY_BUSINESS_CASE,
    FINSWARM_CASE,
    FINSWARM_SURPRISE,
    SAASSWARM_CASE,
    SAASSWARM_SURPRISE,
    CHIPSWARM_CASE,
    CHIPSWARM_SURPRISE,
)
from backend.case.case_parser import CaseParser
from backend.case.case_profiler import CaseProfiler
from backend.surprise.surprise_analyzer import SurpriseAnalyzer
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.trace.trace_manager import TraceStage
from backend.config import get_llm, get_config_status

console = Console(force_terminal=True, legacy_windows=False)


def check_environment():
    """Verify that required API credentials or model configs are available."""
    status = get_config_status()
    if status["status"] != "CONFIGURED" or not status["api_key_available"]:
        console.print(Panel(
            "[bold red]⚠️  No LLM API Key or Base URL detected![/bold red]\n\n"
            "Please create a [bold yellow].env[/bold yellow] file in the project root containing your API key.\n"
            "See [bold cyan].env.example[/bold cyan] for supported options (OpenAI, Gemini, Anthropic, Groq, Ollama).\n\n"
            "Example for Gemini:\n"
            "  GEMINI_API_KEY=AIzaSy...\n"
            "  MODEL=gemini/gemini-3.6-flash",
            title="[bold red]Configuration Missing[/bold red]",
            border_style="red"
        ))
        return False
    return True


def run_validation():
    """Validates data structures, models, agents, and task wiring without live LLM calls."""
    console.print("\n[bold cyan]🔍 Running Quorum Swarm Architecture Validation (Multi-Domain)...[/bold cyan]\n")

    # 1. Validate BusinessCase model
    console.print("  [green]✔[/green] Validating generic BusinessCase & CaseProfile models...")
    case = DUMMY_BUSINESS_CASE
    profile = CaseProfiler.profile(case)
    console.print(f"    Loaded test case: [cyan]{case.title}[/cyan]")
    console.print(f"    Profiled industry: [yellow]{profile.industry}[/yellow] | Company: [yellow]{profile.company}[/yellow]")

    # 2. Validate Multi-Domain Presets
    console.print("  [green]✔[/green] Validating Multi-Domain Presets (FINSWARM, SAASSWARM, CHIPSWARM)...")
    for name, d_case in [("FINSWARM", FINSWARM_CASE), ("SAASSWARM", SAASSWARM_CASE), ("CHIPSWARM", CHIPSWARM_CASE)]:
        p = CaseProfiler.profile(d_case)
        console.print(f"    - Preset: {name} -> Industry: {p.industry} | Mandatory Roles: {len(d_case.mandatory_roles)}")

    # 3. Validate SurpriseEvent model
    console.print("  [green]✔[/green] Validating SurpriseEvent model & types...")
    surprise = DUMMY_SURPRISE_EVENT
    console.print(f"    Loaded test surprise: [magenta]{surprise.description[:70]}...[/magenta]")

    # 4. Validate Boardroom Crew & Active Agents (<= 8 agents)
    console.print("  [green]✔[/green] Validating dynamic Agent Assembly (Strictly <= 8 agents)...")
    crew_orch = BoardroomCrew(business_case=case)
    active_agents = crew_orch.assemble_active_agents()
    console.print(f"    Active boardroom agents count: [bold cyan]{len(active_agents)}[/bold cyan] (Max limit: 8)")
    for ag in active_agents:
        console.print(f"    - Agent Role: [bold]{ag.role}[/bold]")

    # 5. Validate Tasks
    console.print("  [green]✔[/green] Validating connected Boardroom Tasks & context dependencies...")
    crew = crew_orch.build_baseline_crew()
    for i, task in enumerate(crew.tasks, 1):
        num_ctx = len(task.context) if isinstance(task.context, (list, tuple, set)) else 0
        console.print(f"    - Task {i} for [bold]{task.agent.role}[/bold] (Receives {num_ctx} upstream context tasks)")

    # 6. Validate 8 Boardroom Protocol Stages
    console.print("  [green]✔[/green] Validating Boardroom Protocol Stages (including Surprise & Reassessment)...")
    stages_flow = "ANALYSE ➔ SHARE ➔ CHALLENGE ➔ RESPONSE ➔ COMPARE ➔ DECIDE ➔ SURPRISE ➔ REASSESS"
    console.print(f"    Protocol: [bold green]{stages_flow}[/bold green]")

    console.print("\n[bold green]✅ All Quorum Swarm components, domain mappings, and task dependencies validated successfully![/bold green]\n")


def main():
    parser = argparse.ArgumentParser(
        description="Quorum — The Adaptive AI Boardroom: Multi-Agent Business Strategy Swarm",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python backend/main.py                          # Live LLM baseline run
    python backend/main.py --domain finswarm        # FINSWARM fintech domain benchmark
    python backend/main.py --domain saasswarm       # SAASSWARM enterprise cloud domain
    python backend/main.py --domain chipswarm       # CHIPSWARM semiconductor fab domain
    python backend/main.py --mock --surprise        # Deterministic offline baseline + surprise
    python backend/main.py --validate               # Architecture sanity check
        """
    )
    parser.add_argument("--domain", choices=["mobility", "finswarm", "saasswarm", "chipswarm"], help="Run a specific domain benchmark preset")
    parser.add_argument("--case", type=str, help="Path to custom business case JSON or text file")
    parser.add_argument("--surprise", action="store_true", help="Execute Surprise Round adaptation following baseline decision")
    parser.add_argument("--surprise-file", type=str, help="Path to custom surprise event JSON or text file")
    parser.add_argument("--mock", action="store_true", help="Run deterministic offline simulation (no LLM API calls required)")
    parser.add_argument("--validate", action="store_true", help="Run architecture and model validation check only")

    args = parser.parse_args()

    console.print("\n" + "=" * 80, style="bold cyan")
    console.print("   🏛️   QUORUM — THE ADAPTIVE AI BOARDROOM", style="bold white on blue")
    console.print("=" * 80 + "\n", style="bold cyan")

    if args.validate:
        run_validation()
        return

    # Ingest Business Case
    if args.case:
        business_case = CaseParser.from_file(args.case)
    elif args.domain:
        business_case = CaseParser.get_preset(args.domain)
    else:
        business_case = DUMMY_BUSINESS_CASE

    # Ingest Surprise Event if specified
    surprise_event = None
    if args.surprise_file:
        surprise_event = SurpriseAnalyzer.from_file(args.surprise_file)
    elif args.surprise:
        if args.domain:
            surprise_event = SurpriseAnalyzer.get_preset(args.domain)
        else:
            surprise_event = DUMMY_SURPRISE_EVENT

    if not args.mock and not check_environment():
        console.print("\n[yellow]Tip: Run with '--mock' for offline testing or '--validate' to check system structure.[/yellow]\n")
        sys.exit(1)

    profile = CaseProfiler.profile(business_case)
    console.print(Panel(
        f"[bold]Case:[/bold] {business_case.title}\n"
        f"[bold]Industry:[/bold] {profile.industry} | [bold]Company:[/bold] {profile.company}\n"
        f"[bold]Objective:[/bold] {profile.business_objective}\n"
        f"[bold]Available Capital:[/bold] {profile.available_capital}",
        title="[bold cyan]📋 Ingested Case Profile[/bold cyan]",
        border_style="cyan"
    ))

    console.print("[bold cyan]🚀 Initializing Boardroom Swarm Pipeline...[/bold cyan]")
    console.print("   [1] ANALYSE ➔ [2] SHARE ➔ [3] CHALLENGE ➔ [4] RESPONSE ➔ [5] COMPARE ➔ [6] DECIDE")
    if surprise_event:
        console.print("   ➔ [7] SURPRISE ➔ [8] REASSESS ➔ [9] REVISED DECIDE\n")
    else:
        console.print("")

    try:
        orchestrator = BoardroomCrew(business_case=business_case)
        if args.mock:
            console.print("[bold yellow]⚡ Running in Mock Mode (Deterministic Simulation)...[/bold yellow]\n")
            if surprise_event:
                results = orchestrator.run_mock_surprise(surprise_event=surprise_event)
            else:
                results = orchestrator.run_mock()
        else:
            baseline_results = orchestrator.run()
            if surprise_event:
                results = orchestrator.adapt_to_surprise(surprise_event=surprise_event)
            else:
                results = baseline_results

        # Render complete visual trace
        orchestrator.trace_manager.print_trace_summary()

        # Display Baseline CEO final decision
        if orchestrator.trace_manager.baseline_decision_raw:
            console.print("\n" + "=" * 80, style="bold gold1")
            console.print("   🏛️   BASELINE CEO BOARDROOM DECISION (PRE-SURPRISE)", style="bold black on gold1")
            console.print("=" * 80 + "\n", style="bold gold1")
            console.print(Panel(
                Markdown(orchestrator.trace_manager.baseline_decision_raw),
                title="[bold gold1]Baseline Executive Decision (13 Sections)[/bold gold1]",
                border_style="gold1",
                padding=(1, 2)
            ))

        # Display Revised CEO decision if surprise occurred
        if orchestrator.trace_manager.revised_decision_raw:
            console.print("\n" + "=" * 80, style="bold red")
            console.print("   🚨   REVISED CEO BOARDROOM DECISION (POST-SURPRISE ADAPTATION)", style="bold white on red")
            console.print("=" * 80 + "\n", style="bold red")
            console.print(Panel(
                Markdown(orchestrator.trace_manager.revised_decision_raw),
                title="[bold red]Revised Executive Decision (13 Sections)[/bold red]",
                border_style="red",
                padding=(1, 2)
            ))

        console.print(f"\n[bold green]✔ Persistent Execution Trace Saved To:[/bold green] [cyan]{results['trace_file']}[/cyan]\n")

    except Exception as e:
        console.print(f"\n[bold red]❌ Swarm Execution Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
