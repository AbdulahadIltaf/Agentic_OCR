import os
from pathlib import Path
from src.pipeline.preprocess import preprocess
from src.pipeline.ocr        import run_ocr
from src.pipeline.formatter  import format_blocks
from src.pipeline.exporter   import export_docx

data_dir = Path(r"d:\MyStuff\OtherStuff\PPIT\Project\Data")
out_dir  = Path(r"d:\MyStuff\OtherStuff\PPIT\Project\implementation\OCRResults")
out_dir.mkdir(parents=True, exist_ok=True)

for img_file in data_dir.glob("*.jpeg"):
    print(f"Processing {img_file.name}...")
    try:
        img    = preprocess(str(img_file))
        json_list = run_ocr(img)
        
        if not json_list:
            print(f"  -> WARNING: No text detected in {img_file.name}")
            continue
            
        paras  = format_blocks(json_list, img.width)
        
        out_path = out_dir / img_file.with_suffix(".docx").name
        export_docx(paras, str(out_path))
        print(f"  -> Saved {out_path.name}")
        
    except Exception as e:
        print(f"  -> ERROR processing {img_file.name}: {e}")

print(f"Done processing Data folder. Results in {out_dir}")
