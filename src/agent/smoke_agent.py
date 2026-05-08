import os
os.environ["SMOKE_MODE"] = "1"   # signals loop.py to skip input()

from PIL import Image, ImageDraw
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
# need to make sure img is saved where script runs or pass full path
img = Image.new("RGB", (400, 100), "white")
ImageDraw.Draw(img).text((10, 35), "Invoice Total 500", fill="black")
img.save("smoke_src.png")

# patch MAX_RETRIES to 0 to bypass CLI input() block
import src.config as _cfg; _cfg.MAX_RETRIES = 0

from src.agent.loop import run_agent
result = run_agent("smoke_src.png", "smoke_agent_out.docx")
from pathlib import Path
assert Path("smoke_agent_out.docx").exists(), "Agent export failed"
print("AGENT SMOKE PASS")
print(result)
