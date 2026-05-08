import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import MAX_RETRIES
from agent.perceive import perceive
from agent.decide   import decide
from agent.act      import act
from agent.memory   import log_session

def run_agent(img_path: str, out_path: str) -> str:
    """
    Agentic loop: Observe→Interpret→Decide→Act→Learn.
    CLI-only: retry via stdin. GUI: replace input() with tkinter dialog.
    """
    import os
    path = img_path
    for attempt in range(MAX_RETRIES + 1):
        img, json_list = perceive(path)
        decision = decide(json_list)
        if not decision["retry"]:
            break
        if attempt < MAX_RETRIES:
            if os.environ.get("SMOKE_MODE") == "1":
                break # Bypass input in smoke test
            path = input(f"Low confidence ({decision['mean_conf']}). Re-upload path: ")
            
    result = {"attempt": attempt + 1, **decision, "out": out_path}
    log_session(result)
    out = act(img, json_list, decision, out_path)
    return f"AGENT COMPLETE -> {out} | conf={decision['mean_conf']}"
