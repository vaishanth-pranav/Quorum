# 🏛️ QUORUM — The Adaptive AI Boardroom
**Autonomous Multi-Agent Swarm for High-Stakes Business Strategy & Surprise Adaptation**

---

## 1. Team Name & Member Names
- **Team Name:** Quorum
- **Team Members:**
  1. Vaishanth Pranav C S
  2. Sai Adithya K
  3. Surya R


---

## 2. Selected Challenge & Solution Summary
- **Selected Challenge:** Autonomous Multi-Agent Swarm for Executive Strategy Formulation, Conflict Resolution, and Dynamic Surprise Adaptation.
- **One-Paragraph Solution Summary:**  
  **Quorum** is a domain-adaptive multi-agent boardroom platform that autonomously formulates, stress-tests, and executes defensible corporate strategies for any runtime business case (including FinTech credit, enterprise SaaS, semiconductor manufacturing, mobility infrastructure, and synthetic domains). Operating strictly within a 4-to-8 agent capacity ceiling, Quorum executes a rigorous 8-stage deliberation protocol ($\text{ANALYSE} \rightarrow \text{SHARE} \rightarrow \text{CHALLENGE} \rightarrow \text{RESPONSE} \rightarrow \text{COMPARE} \rightarrow \text{DECIDE} \rightarrow \text{SURPRISE} \rightarrow \text{REASSESS}$). It couples large language model domain reasoning with deterministic Python calculation engines to eliminate arithmetic hallucinations and strictly enforce hard constraints (`PASS`, `FAIL`, `INFEASIBLE`). When injected with mid-run disruption shocks, Quorum isolates invalidated assumptions, reruns only materially affected specialist roles, and outputs both a preserved baseline and a revised 13-section Executive Decision with full JSON execution auditability.

---

## 3. Agent List: Roles, Inputs, and Outputs
Quorum maintains an 8-capability pool and dynamically instantiates between 4 and 8 active agents customized to the active case:

| # | Agent Role / Title | Core Capability & Focus | Inputs | Visible Outputs |
|---|---|---|---|---|
| 1 | **Business Research Analyst** | Market intelligence, competitor moats, customer discovery | Case brief markdown, industry facts, market signals | **Evidence-Based Market Intelligence Report** with explicit `[FACT]`, `[ASSUMPTION]`, and `[NOT PROVIDED]` tags |
| 2 | **Chief Financial Officer (CFO)** | Unit economics, CapEx/OpEx, cash runway, break-even timelines | Research intel, financial constraints, capital pools | **Financial Feasibility Model & Capital Allocation Plan** with runway analysis and hard budget checks |
| 3 | **Chief Marketing & Commercial Officer (CMO)** | Go-to-market channels, CAC/LTV dynamics, pipeline conversion | Research report, customer segment data | **Commercial & GTM Acquisition Strategy** with customer conversion economics |
| 4 | **Head of Operations & Infrastructure** | Execution lead times, capacity bottlenecks, supply chain | Procurement constraints, engineering capacity | **Operational Feasibility & Delivery Roadmap** with critical path lead-time safeguards |
| 5 | **Chief Risk Officer & Reviewer (CRO)** | Adversarial stress-testing, flaw detection, strategy comparison | All department reports from `SHARE` stage | **Formal Adversarial Challenge** & **6-Dimension Strategy Comparison Matrix** |
| 6 | **Chief Product & Strategy Officer** | Product architecture, feature packaging, tech roadmap | Market discovery, engineering capacity | **Product Architecture & Roadmap Report** |
| 7 | **Chief Compliance & Quality Officer** | Regulatory standards, disclosures, quality certifications | Regulatory constraints, compliance rules | **Regulatory Compliance Audit & Quality Checklist** |
| 8 | **Chief Executive Officer (CEO)** | Synthesis, constraint reconciliation, definitive mandate | All specialist reports, CRO Challenge, CFO Response, Strategy Matrix | **13-Section QUORUM Executive Decision** with Pass/Fail audits, trade-offs, and $\ge 3$ measurable KPIs |

---

## 4. Installation & Execution Instructions

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Internet access for live LLM API calls (or run offline with `--mock`)

### 1. Environment Setup
```powershell
# Clone repository and navigate to root
cd d:\hackathons\Quorum

# Activate virtual environment
.\crewai-venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys (for Live Runs)
Copy `.env.example` to `.env` and provide your API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL=gemini/gemini-3.7-flash
```

### 3. Execution Commands
```powershell
# 1. Launch Modern Web Cockpit UI
python run_frontend.py
# Open browser at http://127.0.0.1:8000/

# 2. Run Domain Benchmark Presets (CLI)
python backend/main.py --domain finswarm --surprise --mock    # FinTech Digital Credit
python backend/main.py --domain saasswarm --surprise --mock   # Enterprise Cloud SaaS
python backend/main.py --domain chipswarm --surprise --mock   # Semiconductor Foundry

# 3. Ingest Custom Competition Case & Surprise JSON
python backend/main.py --case my_case.json --surprise-file my_surprise.json

# 4. Live LLM Execution (Google Gemini 3.7 Flash)
python backend/main.py --domain finswarm --surprise

# 5. Architecture & Pipeline Sanity Validation
python backend/main.py --validate
```

### 4. Running Test Suites
```powershell
# Multi-Domain Adaptive Swarm Tests (10/10)
python tests/test_domain_adaptive_swarm.py

# Phase 3 Surprise Adaptation Tests (10/10)
python tests/test_phase3_surprise.py

# Phase 2 Boardroom Collaboration Tests (8/8)
python tests/test_phase2_collaboration.py

# Baseline Core Unit Tests (3/3)
python tests/test_swarm_baseline.py
```

---

## 5. Models, Frameworks, Datasets & External Services Used

- **LLM & Reasoning Engine:** Google Gemini (`gemini/gemini-3.7-flash` / `gemini/gemini-2.5-flash`), LiteLLM unified interface.
- **Agent Orchestration Framework:** `crewai==1.15.18` & `crewai-tools==1.15.18`.
- **Backend Web Server:** `FastAPI` + `Uvicorn` asynchronous REST API.
- **Frontend Cockpit:** Vue.js 3 + `marked.js` with custom glassmorphism styling.
- **Validation & Data Typing:** `pydantic>=2.10.0`.
- **CLI Terminal Visualization:** `rich>=13.0.0`.
- **Datasets & Test Fixtures:**
  - `AeroCharge Mobility`: EV fleet charging infrastructure vs SaaS expansion.
  - `FinSwarm (FinTech)`: SME embedded factoring credit lines vs consumer microloans.
  - `SaaSSwarm (B2B SaaS)`: Dedicated single-tenant enterprise VPC vs self-serve PLG.
  - `ChipSwarm (Semiconductor)`: Fab 7 28nm automotive vs 5nm HPC wafer allocation.
  - Synthetic case generators for unseen aerospace/biotech business cases.

---

## 6. Known Limitations & Failure-Handling Behaviour

1. **Rate Limiting / LLM Spikes (503 / 429 Errors):**
   - *Handling:* Quorum incorporates deterministic offline fallback simulation (`--mock`) allowing 100% of pipeline stages, calculations, and strategy matrices to run offline without API connectivity.
2. **Missing Case Brief Facts (Anti-Hallucination):**
   - *Handling:* When a business brief omits critical data (e.g. churn rate, discount rate), agents are strictly barred from fabricating numbers. Missing facts are labeled `UNKNOWN / NOT PROVIDED IN ACTIVE TEST CASE`.
3. **Hard Constraint Breaches (Budget / Break-Even Limits):**
   - *Handling:* The deterministic calculation engine validates CapEx, burn rate, and runway. Any strategy exceeding budget or runway limits is flagged `INFEASIBLE`, barring the CEO from selecting it.
4. **Surprise Blast Radius Containment:**
   - *Handling:* Mid-run disruption shocks trigger impact analysis that reruns only materially affected specialist departments, preserving valid upstream work and avoiding total swarm restarts.
5. **Windows Terminal Character Encoding:**
   - *Handling:* Console outputs and trace files explicitly reconfigure stdout to `utf-8` to prevent `cp1252` encoding errors.

---

## 7. Declaration of Pre-existing or Reused Components

- **Open-Source Frameworks & Libraries:**
  - `CrewAI` (v1.15.18): Agent, Task, and Crew execution abstraction.
  - `LiteLLM`: Model abstraction layer for Gemini, OpenAI, Anthropic, and Groq.
  - `FastAPI` & `Uvicorn`: HTTP API server and static asset hosting.
  - `Pydantic` (v2): Data modeling and validation schemas.
  - `Rich`: Terminal formatting, panels, and Markdown rendering.
  - `Vue.js` & `marked.js`: Client-side UI state management and Markdown parsing.
- **Proprietary & Original Components Built for Quorum:**
  - Dynamic 20-Dimension `CaseProfiler` with anti-hallucination labeling.
  - `DomainMapper` dynamic agent allocation layer (enforcing $\le 8$ agents).
  - Deterministic `CalculationEngine` & `ConstraintValidator` (`PASS`/`FAIL`/`INFEASIBLE`).
  - Targeted `ImpactMapper` for mid-run surprise shock isolation.
  - 13-Section QUORUM Executive Decision task schema and dual baseline/revised trace persistence.
