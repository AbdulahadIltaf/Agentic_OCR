import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from pipeline.preprocess import preprocess
from pipeline.ocr        import run_ocr

def perceive(path: str) -> tuple[object, list]:
    """Load image at path → (PIL Image, JSON list)."""
    img = preprocess(path)
    json_list = run_ocr(img)
    return img, json_list
