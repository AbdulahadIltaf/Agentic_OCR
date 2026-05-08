import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LOG_PATH

def log_session(result: dict) -> None:
    """Append result dict to confidence_log.json."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if LOG_PATH.exists():
        history = json.loads(LOG_PATH.read_text())
    history.append(result)
    LOG_PATH.write_text(json.dumps(history, indent=2))
