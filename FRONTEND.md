# Quorum Frontend

A lightweight Vue 3 browser UI is included in `frontend/` and is served by the FastAPI layer.

## Run

From the project root with the virtual environment active:

```powershell
pip install -r requirements.txt
python run_frontend.py
```

Open `http://127.0.0.1:8000`.

## Modes

- **Mock**: deterministic offline Quorum execution; ideal for demos and testing.
- **Live**: uses the configured LLM from `.env` and the existing CrewAI orchestrator.

For an unseen competition case, select **Custom / unseen case**, paste the complete case, and paste the surprise when it is revealed. The frontend does not hardcode FinSwarm, SaaSSwarm, or ChipSwarm decision logic.
