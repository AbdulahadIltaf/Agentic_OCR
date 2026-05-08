from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.formatter import format_blocks
from pipeline.exporter  import export_docx

def act(img, json_list, decision: dict, out_path: str) -> Path:
    """Format + export .docx if decision is export; else raise."""
    if decision["action"] != "export":
        raise ValueError(f"Agent aborted: conf={decision['mean_conf']}")
    paras = format_blocks(json_list, img.width)
    export_docx(paras, out_path)
    return Path(out_path)
