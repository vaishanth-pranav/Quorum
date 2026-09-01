"""
Configuration and environment manager for Quorum.
Loads environment variables and initializes the CrewAI LLM instance based on provider priority:
1. Explicit MODEL / OPENAI_MODEL_NAME if provided (defaulting to gemini/gemini-3.7-flash).
2. GEMINI_API_KEY -> gemini/gemini-3.7-flash.
3. OPENAI_API_KEY -> gpt-4o-mini.
4. ANTHROPIC_API_KEY -> anthropic/claude-3-5-haiku-20241022.
5. GROQ_API_KEY -> groq/llama-3.3-70b-versatile.
6. OPENAI_API_BASE -> local/custom proxy endpoint.
7. Clear configuration error if no provider credentials exist.
"""


import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from crewai import LLM

# Load .env from workspace root if available
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
else:
    load_dotenv()


def _clean_key(val: Optional[str]) -> Optional[str]:
    """Helper to ensure placeholder keys from templates are not treated as valid."""
    if not val:
        return None
    cleaned = val.strip()
    if cleaned.lower().startswith("your_") or cleaned.lower() in ("na", "none", ""):
        return None
    return cleaned


def resolve_llm_settings() -> Tuple[str, Optional[str], Optional[str], str]:
    """
    Determines the target model, matching provider API key, base URL, and provider name.
    
    Returns:
        (model_name, api_key, api_base, provider_name)
        
    Raises:
        ValueError: If no valid API key or endpoint is configured.
    """
    explicit_model = os.getenv("MODEL") or os.getenv("OPENAI_MODEL_NAME")
    gemini_key = _clean_key(os.getenv("GEMINI_API_KEY"))
    openai_key = _clean_key(os.getenv("OPENAI_API_KEY"))
    anthropic_key = _clean_key(os.getenv("ANTHROPIC_API_KEY"))
    groq_key = _clean_key(os.getenv("GROQ_API_KEY"))
    api_base = _clean_key(os.getenv("OPENAI_API_BASE"))

    # If explicit model is specified, resolve the matching key based on prefix/name
    if explicit_model:
        model_lower = explicit_model.lower()
        if model_lower.startswith(("gemini/", "google/")):
            api_key = gemini_key or openai_key
            provider = "Google Gemini"
        elif model_lower.startswith(("anthropic/", "claude")):
            api_key = anthropic_key
            provider = "Anthropic"
        elif model_lower.startswith("groq/"):
            api_key = groq_key
            provider = "Groq"
        elif model_lower.startswith(("ollama/", "local/")):
            api_key = openai_key or "NA"
            provider = "Ollama / Local"
        else:
            api_key = openai_key or gemini_key or anthropic_key or groq_key
            provider = "OpenAI / Custom"

        if not api_key and not api_base:
            raise ValueError(
                f"Explicit model '{explicit_model}' configured, but no corresponding API key "
                f"found in environment or .env file."
            )
        return explicit_model, api_key, api_base, provider

    # Priority 2: Gemini
    if gemini_key:
        default_gemini = os.getenv("GEMINI_MODEL") or "gemini/gemini-3.7-flash"
        return default_gemini, gemini_key, api_base, "Google Gemini"


    # Priority 3: OpenAI
    if openai_key:
        return "gpt-4o-mini", openai_key, api_base, "OpenAI"

    # Priority 4: Anthropic
    if anthropic_key:
        return "anthropic/claude-3-5-haiku-20241022", anthropic_key, api_base, "Anthropic"

    # Priority 5: Groq
    if groq_key:
        return "groq/llama-3.3-70b-versatile", groq_key, api_base, "Groq"

    # Priority 6: Custom Base URL / Local (e.g. Ollama)
    if api_base:
        return "ollama/llama3.2", openai_key or "NA", api_base, "Local Endpoint (Ollama)"

    # No credentials found
    raise ValueError(
        "No LLM credentials configured. Please set GEMINI_API_KEY, OPENAI_API_KEY, "
        "ANTHROPIC_API_KEY, or GROQ_API_KEY in your .env file."
    )


def get_llm() -> LLM:
    """
    Returns a configured CrewAI LLM instance using the resolved provider and credentials.
    """
    model_name, api_key, api_base, _ = resolve_llm_settings()
    temperature = float(os.getenv("LLM_TEMPERATURE", "0.2"))

    kwargs: Dict[str, Any] = {
        "model": model_name,
        "temperature": temperature,
    }

    if api_key:
        kwargs["api_key"] = api_key
    if api_base:
        kwargs["base_url"] = api_base

    return LLM(**kwargs)


def get_config_status() -> Dict[str, Any]:
    """
    Returns non-sensitive configuration diagnostics without exposing raw API keys.
    """
    try:
        model_name, api_key, api_base, provider = resolve_llm_settings()
        return {
            "status": "CONFIGURED",
            "provider": provider,
            "model": model_name,
            "api_key_available": bool(api_key and api_key != "NA"),
            "custom_base_url": bool(api_base),
            "error": None,
        }
    except Exception as e:
        return {
            "status": "UNCONFIGURED",
            "provider": None,
            "model": None,
            "api_key_available": False,
            "custom_base_url": bool(os.getenv("OPENAI_API_BASE")),
            "error": str(e),
        }


def is_verbose() -> bool:
    """Check if verbose output is enabled."""
    return os.getenv("CREWAI_VERBOSE", "true").lower() in ("true", "1", "yes")


def get_trace_dir() -> Path:
    """Get the output directory for trace logs."""
    trace_dir = Path(os.getenv("TRACE_OUTPUT_DIR", str(ROOT_DIR / "backend" / "trace" / "runs")))
    trace_dir.mkdir(parents=True, exist_ok=True)
    return trace_dir
