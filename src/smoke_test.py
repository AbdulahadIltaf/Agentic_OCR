from PIL import Image, ImageDraw, ImageFont
img = Image.new("RGB", (400, 100), "white")
draw = ImageDraw.Draw(img)
draw.text((10, 30), "Hello World", fill="black")   # default font acceptable
img.save("test_input.png")

from pathlib import Path
from pipeline.preprocess import preprocess
from pipeline.ocr        import run_ocr
from pipeline.formatter  import format_blocks
from pipeline.exporter   import export_docx

pil_img = preprocess("test_input.png")
json_list = run_ocr(pil_img)
paras   = format_blocks(json_list, pil_img.width)
out     = Path("test_output.docx")
export_docx(paras, str(out))
assert out.exists(), "Export failed"
print("SMOKE PASS")
