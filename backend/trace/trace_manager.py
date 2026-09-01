"""
Trace Manager for Quorum execution logging and transparent inspection.
Tracks the complete Boardroom Protocol Stages across Baseline and Surprise Rounds:
ANALYSE -> SHARE -> CHALLENGE -> RESPONSE -> COMPARE -> DECIDE -> SURPRISE -> REASSESS -> DECIDE
Saves structured JSON traces preserving both Baseline and Revised CEO Decisions for third-party auditing.
"""

import sys
import json
import time
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from ..config import get_trace_dir
from ..models.business_case import BusinessCase, SurpriseEvent


class TraceStage(str, Enum):
    ANALYSE = "ANALYSE"
    SHARE = "SHARE"
    CHALLENGE = "CHALLENGE"
    RESPONSE = "RESPONSE"
    COMPARE = "COMPARE"
    DECIDE = "DECIDE"
    SURPRISE = "SURPRISE"
    REASSESS = "REASSESS"


class AgentExecutionRecord:
    def __init__(
        self,
        stage: TraceStage,
        agent_name: str,
        agent_role: str,
        task_name: str,
        input_context: str,
        output: str
    ):
        self.stage = stage
        self.agent_name = agent_name
        self.agent_role = agent_role
        self.task_name = task_name
        self.input_context = input_context
        self.output = output
        self.timestamp = datetime.utcnow().isoformat() + "Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "stage": self.stage.value if isinstance(self.stage, TraceStage) else str(self.stage),
            "agent_name": self.agent_name,
            "agent_role": self.agent_role,
            "task_name": self.task_name,
            "timestamp": self.timestamp,
            "input_context_preview": self.input_context[:300] + "..." if len(self.input_context) > 300 else self.input_context,
            "output": self.output,
        }


class TraceManager:
    """
    Manages persistent trace recording and terminal visualization of the multi-agent boardroom swarm.
    Preserves both BASELINE and REVISED decisions side-by-side.
    """

    def __init__(self, business_case: BusinessCase):
        self.business_case = business_case
        self.surprise_event: Optional[SurpriseEvent] = None
        self.start_time = time.time()
        self.start_timestamp = datetime.utcnow().isoformat() + "Z"
        self.records: List[AgentExecutionRecord] = []
        self.baseline_decision_raw: Optional[str] = None
        self.revised_decision_raw: Optional[str] = None
        self.console = Console(force_terminal=True, legacy_windows=False)

    def record_event(
        self,
        stage: TraceStage,
        agent_name: str,
        agent_role: str,
        task_name: str,
        input_context: str,
        output: str
    ):
        record = AgentExecutionRecord(
            stage=stage,
            agent_name=agent_name,
            agent_role=agent_role,
            task_name=task_name,
            input_context=input_context,
            output=output
        )
        self.records.append(record)

    def record_agent_output(
        self,
        agent_name: str,
        agent_role: str,
        task_name: str,
        input_context: str,
        output: str,
        stage: Optional[TraceStage] = None
    ):
        """Backward-compatible helper that infers or assigns the stage."""
        if stage is None:
            if "Surprise" in task_name or "reassess" in task_name.lower():
                stage = TraceStage.REASSESS
            elif "Risk" in agent_role or "Reviewer" in agent_role:
                stage = TraceStage.CHALLENGE
            elif "CEO" in agent_role:
                stage = TraceStage.DECIDE
            elif "Response" in task_name or "Defense" in task_name:
                stage = TraceStage.RESPONSE
            elif "Compare" in task_name or "Comparison" in task_name:
                stage = TraceStage.COMPARE
            else:
                stage = TraceStage.ANALYSE
        self.record_event(stage, agent_name, agent_role, task_name, input_context, output)

    def record_share_event(self, shared_findings_summary: str, recipient_agents: List[str]):
        """Records an explicit SHARE stage trace event showing cross-department information exchange."""
        recipients_str = ", ".join(recipient_agents)
        self.record_event(
            stage=TraceStage.SHARE,
            agent_name="Boardroom Orchestrator",
            agent_role="Shared State Coordinator",
            task_name="Boardroom Information Sharing & State Distribution",
            input_context=f"Aggregated department findings dispatched to: {recipients_str}",
            output=shared_findings_summary
        )

    def record_surprise_event(self, surprise_event: SurpriseEvent):
        """Records an explicit SURPRISE stage event documenting the injected mid-event perturbation."""
        self.surprise_event = surprise_event
        self.record_event(
            stage=TraceStage.SURPRISE,
            agent_name="Competition Organizer / Injected Event",
            agent_role="External Market Shock",
            task_name=f"Surprise Round Ingestion: [{surprise_event.type.value.upper()}]",
            input_context=f"Surprise ID: {surprise_event.id} | Severity: {surprise_event.severity}",
            output=surprise_event.to_brief_markdown()
        )

    def set_final_decision(self, raw_decision: str):
        """Sets the initial/baseline decision (backward-compatible)."""
        self.baseline_decision_raw = raw_decision

    def set_baseline_decision(self, raw_decision: str):
        """Explicitly sets the baseline decision."""
        self.baseline_decision_raw = raw_decision

    def set_revised_decision(self, raw_decision: str):
        """Sets the revised decision generated after the surprise round."""
        self.revised_decision_raw = raw_decision

    def get_stages_present(self) -> List[str]:
        """Returns the list of unique trace stages recorded in order."""
        return [r.stage.value if isinstance(r.stage, TraceStage) else str(r.stage) for r in self.records]

    def save_trace(self) -> Path:
        """Save the execution trace to a structured JSON file."""
        trace_dir = get_trace_dir()
        duration_seconds = round(time.time() - self.start_time, 2)

        unique_stages = []
        for r in self.records:
            s_val = r.stage.value if isinstance(r.stage, TraceStage) else str(r.stage)
            if s_val not in unique_stages:
                unique_stages.append(s_val)

        trace_data = {
            "session_metadata": {
                "system": "Quorum — The AI Boardroom",
                "version": "Phase 3 Surprise Round Adaptation",
                "protocol_sequence": unique_stages,
                "timestamp_start": self.start_timestamp,
                "timestamp_end": datetime.utcnow().isoformat() + "Z",
                "duration_seconds": duration_seconds,
                "total_trace_events": len(self.records),
                "surprise_round_executed": self.surprise_event is not None,
            },
            "business_case": self.business_case.model_dump(),
            "surprise_event": self.surprise_event.model_dump() if self.surprise_event else None,
            "agent_execution_trace": [r.to_dict() for r in self.records],
            "baseline_decision": self.baseline_decision_raw,
            "revised_decision": self.revised_decision_raw,
            # Backward-compatibility pointer
            "final_decision": self.revised_decision_raw or self.baseline_decision_raw,
        }

        # Save timestamped trace file
        timestamp_slug = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = trace_dir / f"trace_{timestamp_slug}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2, ensure_ascii=False)

        # Save latest pointer
        latest_path = trace_dir / "latest_run.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(trace_data, f, indent=2, ensure_ascii=False)

        return filepath

    def print_trace_summary(self):
        """Render a clean, transparent visual overview of all protocol stages in the terminal."""
        self.console.print("\n" + "=" * 80, style="bold cyan")
        self.console.print("   🏛️   QUORUM — BOARDROOM COLLABORATION PROTOCOL TRACE", style="bold white on blue")
        self.console.print("=" * 80 + "\n", style="bold cyan")

        # Business Case Summary Panel
        self.console.print(Panel(
            f"[bold yellow]Title:[/bold yellow] {self.business_case.title}\n"
            f"[bold yellow]Problem:[/bold yellow] {self.business_case.problem[:200]}...\n"
            f"[bold yellow]Objective:[/bold yellow] {self.business_case.objective}",
            title="[bold green]Ingested Business Case Brief[/bold green]",
            border_style="green"
        ))

        if self.surprise_event:
            self.console.print(Panel(
                f"[bold red]Event Type:[/bold red] {self.surprise_event.type.value.upper()} (ID: {self.surprise_event.id})\n"
                f"[bold red]Description:[/bold red] {self.surprise_event.description}\n"
                f"[bold red]Materially Affected Departments:[/bold red] {', '.join(self.surprise_event.affected_departments)}",
                title="[bold red]🚨 Mid-Run Surprise Event Injected[/bold red]",
                border_style="red"
            ))

        # Table of Swarm Execution Sequence with Stage Badges
        table = Table(title="Boardroom Protocol Flow", show_header=True, header_style="bold magenta")
        table.add_column("Step", style="dim", width=6)
        table.add_column("Protocol Stage", style="bold yellow", width=14)
        table.add_column("Agent / Role", style="bold cyan", width=26)
        table.add_column("Task Focus", style="white", width=26)
        table.add_column("Status", style="green", width=10)

        for idx, rec in enumerate(self.records, 1):
            stage_str = rec.stage.value if isinstance(rec.stage, TraceStage) else str(rec.stage)
            table.add_row(
                str(idx),
                f"[{stage_str}]",
                f"{rec.agent_name}\n({rec.agent_role})",
                rec.task_name,
                "COMPLETED"
            )

        self.console.print(table)
        self.console.print("\n")

        # Stage Color Mapping
        stage_colors = {
            TraceStage.ANALYSE: "cyan",
            TraceStage.SHARE: "magenta",
            TraceStage.CHALLENGE: "red",
            TraceStage.RESPONSE: "yellow",
            TraceStage.COMPARE: "blue",
            TraceStage.DECIDE: "green",
            TraceStage.SURPRISE: "red",
            TraceStage.REASSESS: "magenta",
        }

        # Individual Visible Stage Reports
        for idx, rec in enumerate(self.records, 1):
            stage_enum = rec.stage if isinstance(rec.stage, TraceStage) else TraceStage(rec.stage)
            color = stage_colors.get(stage_enum, "blue")
            stage_badge = f"[{stage_enum.value}]"

            self.console.print(Panel(
                Markdown(rec.output),
                title=f"[bold {color}]Step {idx} {stage_badge}: {rec.agent_name} ({rec.agent_role}) — {rec.task_name}[/bold {color}]",
                border_style=color,
                padding=(1, 2)
            ))
            self.console.print("")
