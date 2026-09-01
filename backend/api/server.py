"""
HTTP API Server for Quorum — The Adaptive AI Boardroom Frontend.
Provides endpoints for health checks, domain benchmark presets, case profiling,
and live/mock multi-agent execution with surprise adaptation.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.case.case_parser import CaseParser
from backend.case.case_profiler import CaseProfiler
from backend.surprise.surprise_analyzer import SurpriseAnalyzer
from backend.engine.strategy_evaluator import StrategyEvaluator
from backend.workflows.boardroom_crew import BoardroomCrew
from backend.config import get_config_status


app = FastAPI(title="Quorum API", version="2.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


class RunRequest(BaseModel):
    case_text: Optional[str] = None
    domain: Optional[str] = None
    surprise_text: Optional[str] = None
    mode: str = "mock"
    run_surprise: bool = False


def serialise_surprise(s):
    return s.model_dump() if s else None


def build_payload(orch: BoardroomCrew, result: Dict[str, Any]) -> Dict[str, Any]:
    profile = orch.profile.model_dump()
    records = [r.to_dict() for r in orch.trace_manager.records]
    
    # Generate structured strategy comparison matrix
    matrix_data = None
    try:
        matrix = StrategyEvaluator.evaluate_strategies(orch.business_case, orch.profile)
        matrix_data = matrix.model_dump()
    except Exception:
        matrix_data = None

    return {
        "case": orch.business_case.model_dump(),
        "profile": profile,
        "agents": [
            {
                "role": getattr(a, "role", str(a)),
                "goal": getattr(a, "goal", ""),
                "backstory": getattr(a, "backstory", "")
            }
            for a in orch.assemble_active_agents()
        ],
        "records": records,
        "matrix": matrix_data,
        "baseline_decision": orch.trace_manager.baseline_decision_raw,
        "revised_decision": orch.trace_manager.revised_decision_raw,
        "surprise_event": serialise_surprise(orch.trace_manager.surprise_event),
        "trace_file": result.get("trace_file"),
    }


@app.get("/api/health")
def health():
    status = get_config_status()
    return {
        "ok": True,
        "llm_configured": bool(status.get("api_key_available")),
        "provider": status.get("provider"),
        "model": status.get("model")
    }


@app.get("/api/presets")
def presets():
    return {
        "mobility": {
            "label": "AeroCharge Mobility (EV Infrastructure)",
            "domain": "mobility",
            "case": CaseParser.get_preset("mobility").model_dump(),
            "surprise": SurpriseAnalyzer.get_preset("mobility").model_dump()
        },
        "finswarm": {
            "label": "FinSwarm (Fintech / Credit & Treasury)",
            "domain": "finswarm",
            "case": CaseParser.get_preset("finswarm").model_dump(),
            "surprise": SurpriseAnalyzer.get_preset("finswarm").model_dump()
        },
        "saasswarm": {
            "label": "SaaSSwarm (Enterprise Cloud / SaaS)",
            "domain": "saasswarm",
            "case": CaseParser.get_preset("saasswarm").model_dump(),
            "surprise": SurpriseAnalyzer.get_preset("saasswarm").model_dump()
        },
        "chipswarm": {
            "label": "ChipSwarm (Semiconductor / Foundry Capacity)",
            "domain": "chipswarm",
            "case": CaseParser.get_preset("chipswarm").model_dump(),
            "surprise": SurpriseAnalyzer.get_preset("chipswarm").model_dump()
        },
    }


@app.post("/api/run")
def run_case(req: RunRequest):
    try:
        if req.case_text and req.case_text.strip():
            case = CaseParser.from_text(req.case_text.strip())
        elif req.domain:
            case = CaseParser.get_preset(req.domain)
        else:
            raise HTTPException(400, "Please provide business case text or select a domain preset.")

        surprise = None
        if req.surprise_text and req.surprise_text.strip():
            surprise = SurpriseAnalyzer.from_dict({
                "id": "UI-SURPRISE",
                "type": "unforeseen_shock",
                "description": req.surprise_text.strip(),
                "severity": "HIGH",
                "affected_departments": ["Finance & Economics", "Operations / Engineering", "Risk"],
                "changed_assumptions": ["Baseline operating assumptions altered by shock."],
                "new_numerical_constraints": {}
            })
        elif req.run_surprise and req.domain:
            surprise = SurpriseAnalyzer.get_preset(req.domain)

        orch = BoardroomCrew(case)
        if req.mode == "live":
            result = orch.run()
            if surprise:
                result = orch.adapt_to_surprise(surprise)
        else:
            result = orch.run_mock_surprise(surprise) if surprise else orch.run_mock()

        return build_payload(orch, result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(500, f"Quorum execution failed: {exc}") from exc


FRONTEND = ROOT / "frontend"


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND / "index.html")


@app.get("/{path:path}", include_in_schema=False)
def static_files(path: str):
    target = FRONTEND / path
    if target.exists() and target.is_file():
        return FileResponse(target)
    return FileResponse(FRONTEND / "index.html")
