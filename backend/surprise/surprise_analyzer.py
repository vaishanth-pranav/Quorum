"""
Generic Surprise Analyzer for Quorum.
Parses, categorizes, and validates any unexpected mid-run disruption event.
"""

from typing import Dict, Any, Union
from pathlib import Path
import json
from ..models.business_case import SurpriseEvent, SurpriseType, DUMMY_SURPRISE_EVENT, FINSWARM_SURPRISE, SAASSWARM_SURPRISE, CHIPSWARM_SURPRISE


class SurpriseAnalyzer:
    """Ingests and validates generic surprise events."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SurpriseEvent:
        stype = data.get("type", "unforeseen_shock")
        try:
            enum_type = SurpriseType(stype)
        except ValueError:
            enum_type = SurpriseType.UNFORESEEN_SHOCK

        return SurpriseEvent(
            id=data.get("id", "SURPRISE-CUSTOM-001"),
            type=enum_type,
            description=data.get("description", "An unexpected market disruption occurred."),
            severity=data.get("severity", "HIGH"),
            affected_departments=data.get("affected_departments", ["Finance & Economics", "Risk"]),
            changed_assumptions=data.get("changed_assumptions", ["Baseline market stability assumption invalidated."]),
            new_numerical_constraints=data.get("new_numerical_constraints", {})
        )

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> SurpriseEvent:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Surprise file not found: {path}")

        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(content)
            return cls.from_dict(data)
        else:
            return SurpriseEvent(
                id=f"SURPRISE-{path.stem.upper()}",
                type=SurpriseType.UNFORESEEN_SHOCK,
                description=content.strip(),
                severity="HIGH",
                affected_departments=["Finance & Economics", "Operations / Engineering", "Risk"],
                changed_assumptions=["Baseline operating assumptions altered by shock."]
            )

    @classmethod
    def get_preset(cls, name: str) -> SurpriseEvent:
        lookup = {
            "mobility": DUMMY_SURPRISE_EVENT,
            "default": DUMMY_SURPRISE_EVENT,
            "budget": DUMMY_SURPRISE_EVENT,
            "finswarm": FINSWARM_SURPRISE,
            "credit_spike": FINSWARM_SURPRISE,
            "saasswarm": SAASSWARM_SURPRISE,
            "competitor_price_war": SAASSWARM_SURPRISE,
            "chipswarm": CHIPSWARM_SURPRISE,
            "euv_tool_outage": CHIPSWARM_SURPRISE,
        }
        key = name.strip().lower()
        if key not in lookup:
            raise KeyError(f"Unknown surprise preset '{name}'. Supported: {list(lookup.keys())}")
        return lookup[key]
