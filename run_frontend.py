"""Launch Quorum's web UI."""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("backend.api.server:app", host="127.0.0.1", port=8000, reload=False)
