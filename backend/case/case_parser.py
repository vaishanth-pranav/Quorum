"""
Universal Case Parser for Quorum.
Ingests business cases from raw dicts, JSON files, Markdown text, or plain text briefs.
"""

import json
from pathlib import Path
from typing import Union, Dict, Any
from ..models.business_case import BusinessCase, DUMMY_BUSINESS_CASE, FINSWARM_CASE, SAASSWARM_CASE, CHIPSWARM_CASE


class CaseParser:
    """Parses various case formats into a clean BusinessCase model."""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> BusinessCase:
        return BusinessCase(
            title=data.get("title", "Untitled Business Case"),
            problem=data.get("problem", data.get("problem_statement", "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")),
            objective=data.get("objective", data.get("strategic_objective", "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")),
            context=data.get("context", data.get("background", "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE")),
            constraints=data.get("constraints", []),
            available_data=data.get("available_data", data.get("metrics", {})),
            assumptions=data.get("assumptions", []),
            mandatory_roles=data.get("mandatory_roles", data.get("roles", []))
        )

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> BusinessCase:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Case file not found: {path}")

        content = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            data = json.loads(content)
            return cls.from_dict(data)
        else:
            return cls.from_text(content, title=path.stem)

    @classmethod
    def from_text(cls, text: str, title: str = "Ingested Business Brief") -> BusinessCase:
        """Parses plain or markdown text by scanning section headers or assigning as unstructured brief."""
        lines = text.strip().splitlines()
        problem, objective, context = [], [], []
        constraints, assumptions = [], []
        available_data = {}
        current_sec = "context"

        for line in lines:
            line_str = line.strip()
            lower = line_str.lower()
            if "problem" in lower and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "problem"
                continue
            elif ("objective" in lower or "goal" in lower) and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "objective"
                continue
            elif ("constraint" in lower or "limit" in lower) and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "constraints"
                continue
            elif "assumption" in lower and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "assumptions"
                continue
            elif ("data" in lower or "metric" in lower or "financial" in lower) and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "data"
                continue
            elif ("context" in lower or "background" in lower) and (lower.startswith("#") or lower.endswith(":")):
                current_sec = "context"
                continue

            if not line_str:
                continue

            if current_sec == "problem":
                problem.append(line_str)
            elif current_sec == "objective":
                objective.append(line_str)
            elif current_sec == "constraints":
                constraints.append(line_str.lstrip("-*•0123456789. "))
            elif current_sec == "assumptions":
                assumptions.append(line_str.lstrip("-*•0123456789. "))
            elif current_sec == "data":
                if ":" in line_str:
                    k, v = line_str.split(":", 1)
                    available_data[k.strip().lstrip("-*• ")] = v.strip()
                else:
                    available_data[f"data_point_{len(available_data)+1}"] = line_str
            else:
                context.append(line_str)

        return BusinessCase(
            title=title,
            problem="\n".join(problem) or ("\n".join(lines[:3]) if lines else "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE"),
            objective="\n".join(objective) or "UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE",
            context="\n".join(context) or text,
            constraints=constraints,
            available_data=available_data,
            assumptions=assumptions
        )

    @classmethod
    def get_preset(cls, name: str) -> BusinessCase:
        lookup = {
            "mobility": DUMMY_BUSINESS_CASE,
            "default": DUMMY_BUSINESS_CASE,
            "finswarm": FINSWARM_CASE,
            "fintech": FINSWARM_CASE,
            "lending": FINSWARM_CASE,
            "saasswarm": SAASSWARM_CASE,
            "saas": SAASSWARM_CASE,
            "cloud": SAASSWARM_CASE,
            "chipswarm": CHIPSWARM_CASE,
            "semiconductor": CHIPSWARM_CASE,
            "chips": CHIPSWARM_CASE,
        }
        key = name.strip().lower()
        if key not in lookup:
            raise KeyError(f"Unknown preset '{name}'. Supported: {list(lookup.keys())}")
        return lookup[key]
