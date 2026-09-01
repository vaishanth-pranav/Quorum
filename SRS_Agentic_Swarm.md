# Software Requirements Specification
## Project: AI Boardroom — Agentic Swarm Competition Entry
**Version:** 1.0
**Date:** [fill in event date]
**Team:** [fill in team name / members]

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for a multi-agent AI system ("the Swarm") that simulates a company management team. The system analyses a business problem through specialised department agents, surfaces disagreement between them, and produces a CEO-level decision — then revises that decision when a business "surprise" is introduced.

This SRS exists to keep the build scoped and to make sure every rubric-scored requirement in the official rulebook has a corresponding system requirement.

### 1.2 Scope
The system will:
- Accept a business case (challenge brief) as input.
- Run 4–8 distinct AI agents, each with a department responsibility.
- Produce visible, inspectable intermediate outputs (a trace).
- Surface at least one genuine disagreement between agents.
- Compare at least two viable strategies.
- Produce one final CEO decision with rationale, trade-offs, risks, assumptions, an implementation plan, and KPIs.
- Accept a "surprise" input mid-run and produce a revised decision without a full rebuild.

Out of scope: a polished frontend/UI (optional, not scored directly), payment integrations, real-world data collection beyond what's provided or public.

### 1.3 Definitions
| Term | Meaning |
|---|---|
| Agent | An identifiable AI role with its own instruction, input, and output |
| Swarm | The full set of agents plus coordination/orchestration logic |
| CEO Agent | The agent that resolves conflicts and issues the final decision |
| Trace | The saved record of every agent's inputs/outputs and exchanges |
| Surprise | Organizer-issued mid-event change to the business scenario |

### 1.4 References
- Agentic Swarm Official Participant Rulebook, v1.0 (event source document)

---

## 2. Overall Description

### 2.1 Product Perspective
A standalone, self-contained project (script, notebook, or workflow graph) run locally or via hosted APIs. No dependency on external production systems.

### 2.2 User Roles
- **Team/Operator** — runs the system, feeds in the challenge and surprise, presents to judges.
- **Judge** — inspects trace, may request live changes to inputs or agent instructions.

### 2.3 Assumptions & Constraints
- Business case facts are limited to what's supplied by organizers, public information, or clearly labelled assumptions.
- Debate must be capped at 3 review cycles by default (no infinite loops).
- System must still produce a final result if one non-CEO agent fails.
- No fully hardcoded final outcome (this zeroes two rubric categories).
- Cost neutrality: no credit for premium models/tools — plan for whatever's cheapest/most reliable.

---

## 3. Functional Requirements

### FR-1: Mandatory Agents
The system SHALL implement at minimum these four agents, each with a distinct prompt/role, input, and output:

| ID | Agent | Responsibility | Required Output |
|---|---|---|---|
| FR-1.1 | Business Research | Market, customers, competitors, opportunity, risk | Evidence-based findings |
| FR-1.2 | Finance | Cost, revenue, affordability, profitability, financial risk | Financial recommendation + assumptions |
| FR-1.3 | Marketing & Sales | Target customers, positioning, channels, acquisition | Go-to-market recommendation |
| FR-1.4 | CEO | Compares alternatives, resolves conflict, issues decision | Decision, rationale, actions, KPIs |

Optional agents (Operations, Product, Risk, Compliance, HR, Customer Experience, Reviewer) MAY be added up to a total of 8, only if they materially change the outcome.

### FR-2: Information Exchange
- FR-2.1: Each department agent SHALL receive the business brief as input.
- FR-2.2: Department outputs SHALL be passed as context into at least one other agent (not analysed in total isolation).
- FR-2.3: All exchanges SHALL be logged to a persistent trace (see FR-6).

### FR-3: Disagreement / Challenge
- FR-3.1: The system SHALL produce at least one instance where an agent questions or rejects another agent's material recommendation.
- FR-3.2: The challenged agent SHALL produce a visible response (defend or revise).

### FR-4: Strategy Comparison
- FR-4.1: The swarm SHALL generate and hold at least two viable business strategies before the CEO decides.

### FR-5: CEO Decision Output
The CEO agent's final output SHALL contain all of:
1. One clear decision statement.
2. Department evidence that influenced it.
3. At least one rejected alternative with reason for rejection.
4. Trade-offs, risks, and assumptions.
5. A practical implementation sequence with responsible functions.
6. At least three measurable KPIs.

### FR-6: Execution Trace
- FR-6.1: The system SHALL persist every agent's input and output (JSON, text, or log file).
- FR-6.2: The trace SHALL be reproducible/inspectable by a third party without re-running the whole system.

### FR-7: Termination & Control
- FR-7.1: The system SHALL cap agent debate/review cycles at 3 by default.
- FR-7.2: The workflow SHALL terminate deterministically (no uncontrolled loops).

### FR-8: Failure Handling
- FR-8.1: If any non-CEO agent fails or errors, the system SHALL still produce a final CEO decision (via fallback/default behavior).
- FR-8.2: The fallback behavior SHALL be documented, not silently hidden.

### FR-9: Surprise Adaptation
Given a new business fact mid-run, the system SHALL:
1. Identify which original facts/assumptions changed.
2. Re-run only the agents materially affected.
3. Produce a second boardroom comparison/review.
4. Produce a revised CEO decision.
5. Explain what changed vs. what stayed stable, and why.
6. Update relevant KPIs/budget/implementation steps.
- Constraint: this SHALL NOT require rebuilding the application — only changed inputs/logic.

### FR-10: Assumption Labelling
- Any fact not explicitly supplied SHALL be labelled as an assumption in agent output, not presented as verified fact.

---

## 4. Non-Functional Requirements

| ID | Requirement |
|---|---|
| NFR-1 | **Reproducibility** — another person must be able to run/inspect the project from the submitted instructions alone. |
| NFR-2 | **Transparency** — inputs/outputs of every agent must be visible to judges, not just a final summary. |
| NFR-3 | **Reliability** — system should complete a full run without manual intervention under normal conditions. |
| NFR-4 | **Cost neutrality** — avoid dependence on expensive models/rate-limited APIs that risk failure during live demo; have a cheaper fallback model configured. |
| NFR-5 | **Time-boxing** — full pipeline (baseline) should run within a few minutes to leave room for iteration during the 150-min build window. |
| NFR-6 | **Data hygiene** — no secrets, API keys, or personal data committed to the repo/submission. |

---

## 5. System Architecture (to be filled in during Swarm Design phase)

```
[Business Brief]
      |
      v
[Business Research Agent] --\
                              \
[Finance Agent] ---------------> [Shared State / Trace] --> [Marketing & Sales Agent]
                              /                                        |
                             /                                         v
                    (challenge/response loop, max 3 cycles)      [CEO Agent] --> Final Decision
```
*(Replace with your actual graph once agents/tools are finalised — required for submission as a PNG/PDF/slide.)*

**Suggested implementation:** CrewAI or LangGraph (Python), sequential-then-critique pattern: Research → Finance & Marketing (parallel) → cross-critique → CEO synthesis.

---

## 6. Data Requirements
- Input: challenge pack facts, any provided datasets, publicly available supporting data.
- Output: per-agent JSON/text records; final CEO decision document; KPI list; implementation plan.
- All external data claims traceable to source or labelled as assumption.

---

## 7. Deliverable Mapping (for submission)

| Deliverable | Source in this SRS |
|---|---|
| Source/workflow | Implementation of FR-1 to FR-9 |
| README | Section 1, 2, 5 + agent list from FR-1 |
| Architecture diagram | Section 5 |
| Baseline evidence | Trace from FR-6 pre-surprise |
| Surprise evidence | Trace from FR-6 post-surprise (FR-9) |
| Business summary (≤2 pages) | FR-5 CEO output + KPIs |
| Pitch deck (≤5 slides) | Sections 1, 5, FR-3, FR-9 |

---

## 8. Acceptance Criteria (self-check before submission)
- [ ] 4–8 identifiable agents, each with distinct role/input/output
- [ ] Research, Finance, Marketing & Sales, CEO all present
- [ ] Trace shows exchange + at least one real disagreement + response
- [ ] At least 2 strategies compared
- [ ] CEO output has all 6 required elements (FR-5)
- [ ] Baseline and surprise decisions saved separately
- [ ] Fallback/failure path demonstrated
- [ ] No hardcoded final outcome
- [ ] All reused components/datasets disclosed
- [ ] No secrets or personal data in submission
