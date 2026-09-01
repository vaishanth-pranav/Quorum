# 🏛️ Quorum — The AI Boardroom
**Agentic Multi-Agent Swarm for Executive Decision-Making**

> **Version:** Phase 2 Boardroom Collaboration Protocol  
> **Framework:** Python + CrewAI 1.15.18  

---

## 1. Project Overview

**Quorum** simulates an executive company boardroom powered by an agentic multi-agent swarm. When presented with a complex business challenge brief (`BusinessCase`), Quorum executes a rigorous 6-stage boardroom collaboration protocol:

$$\textbf{ANALYSE} \longrightarrow \textbf{SHARE} \longrightarrow \textbf{CHALLENGE} \longrightarrow \textbf{RESPONSE} \longrightarrow \textbf{COMPARE} \longrightarrow \textbf{DECIDE}$$

The system surfaces genuine cross-departmental friction, executes structured adversarial critiques, captures defenses and revisions, evaluates competing strategies side-by-side, and synthesizes a high-conviction CEO decision backed by measurable KPIs and a persistent JSON execution trace.

---

## 2. The 6 Boardroom Agents

| # | Agent Role | Responsibility | Protocol Stage | Key Deliverable |
|---|---|---|---|---|
| 1 | **Business Research** | Market dynamics, customer sentiment, competitor moats | `ANALYSE` | Evidence-based Market Intelligence Report with explicit assumption tags |
| 2 | **Finance (CFO)** | Unit economics, CapEx/OpEx, cash runway, EBITDA break-even | `ANALYSE` / `RESPONSE` | Financial Feasibility Report & Revised Tranche Capital Allocation |
| 3 | **Marketing & Sales (CMO)** | Positioning, GTM channels, CAC/LTV dynamics | `ANALYSE` | Commercial Strategy & Customer Acquisition Model |
| 4 | **Operations** | Supply chain, grid connection lead times, team capacity | `ANALYSE` | Infrastructure & Execution Delivery Feasibility Report |
| 5 | **Risk / Reviewer (CRO)** | Adversarial stress-test, flaw detection, strategy comparison matrix | `CHALLENGE` / `COMPARE` | Formal Boardroom Challenge & 6-Dimension Strategy Comparison Matrix |
| 6 | **Chief Executive Officer (CEO)** | Executive synthesis, resolves conflicts, rejects alternatives, sets KPIs | `DECIDE` | Definitive Executive Decision Document (with 8 core sections & 3+ KPIs) |

---

## 3. The 6-Stage Collaboration Protocol

```
[1. ANALYSE]
  ├── Business Research Analyst (Market, Competitors, Customer Discovery)
  ├── Finance / CFO (Unit Economics, Burn Rate, Runway, CapEx)
  ├── Marketing & Sales / CMO (Target Accounts, GTM, CAC/LTV)
  └── Operations (Supply Chain, Lead Times, Skill Sets)
        │
        ▼
[2. SHARE]
  └── Synchronizes all 4 department reports into Boardroom Shared State
      Logs explicit SHARE trace event showing cross-department information flow
        │
        ▼
[3. CHALLENGE]
  └── Chief Risk Officer (Adversarial Reviewer)
      Inspects actual department outputs for material flaws / contradictions
      Issues targeted challenge demanding defense or revision
        │
        ▼
[4. RESPONSE]
  └── Challenged Department Agent (e.g. CFO)
      Produces visible response (ACCEPT / REJECT / MODIFY) with updated numbers
        │
        ▼
[5. COMPARE]
  └── Swarm generates & holds at least TWO viable business strategies
      Evaluates: Business Value, Financial Viability, Customer Fit, Ops Feasibility, Risk, Assumptions
        │
        ▼
[6. DECIDE]
  └── CEO Executive Decision
      Synthesizes department findings + Challenge + Response + Strategy Matrix
      Issues definitive mandate with 8 required sections & 3+ measurable KPIs
        │
        ▼
[EXECUTION TRACE]
  └── Persistent JSON trace (backend/trace/runs/*.json) logging all 6 stages
```

---

## 4. Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- Activated virtual environment (`crewai-venv`)

### 1. Installation
```bash
# Windows
.\crewai-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run All Tests
```bash
# Run Phase 2 Boardroom Collaboration test suite (tests all 8 rulebook criteria)
python tests/test_phase2_collaboration.py

# Run baseline unit tests
python tests/test_swarm_baseline.py
```

### 3. Architecture Validation (No API Key Required)
```bash
python backend/main.py --validate
```

### 4. Run Deterministic Mock Swarm (Offline Simulation)
```bash
python backend/main.py --mock
```

### 5. Run Live Swarm with LLM
Configure `.env` with your API key (`OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.):
```bash
python backend/main.py
```

---

## 5. Trace Inspection

Every run outputs a structured JSON trace saved to:
- `backend/trace/runs/latest_run.json`
- `backend/trace/runs/trace_<timestamp>.json`

The trace records the complete protocol sequence:
```json
"protocol_sequence": [
  "ANALYSE",
  "SHARE",
  "CHALLENGE",
  "RESPONSE",
  "COMPARE",
  "DECIDE"
]
```
Each entry captures the stage, agent, task, context preview, timestamp, and full raw output.
