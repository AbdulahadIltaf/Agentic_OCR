import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai


def _resolve_env_file() -> Path:
    """Find API_KEYS/.env relative to repo (no machine-specific hardcoding)."""
    src_dir = Path(__file__).resolve().parent
    impl_dir = src_dir.parent
    repo_root = impl_dir.parent
    candidates = [
        repo_root / "API_KEYS" / ".env",
        impl_dir / ".env",
        Path.cwd() / "API_KEYS" / ".env",
        Path.cwd() / ".env",
    ]
    for p in candidates:
        if p.is_file():
            return p
    return repo_root / "API_KEYS" / ".env"


load_dotenv(dotenv_path=_resolve_env_file())

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("WARNING: GEMINI_API_KEY not set — add API_KEYS/.env at project root or export the variable.")

GEMINI_MODEL = "gemini-1.5-flash"

MAX_RETRIES = 2
LOG_PATH = Path("/tmp/confidence_log.json")
