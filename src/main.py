import tkinter as tk
from tkinter import filedialog
from pathlib import Path

from pipeline.preprocess import preprocess
from pipeline.ocr        import run_ocr
from pipeline.formatter  import format_blocks
from pipeline.exporter   import export_docx

img_path = ""

def open_image():
    """Handle open image button click."""
    global img_path
    img_path = filedialog.askopenfilename(
        filetypes=[("Images","*.jpg *.jpeg *.png *.JPG *.PNG")])
    # FIXME: Spec does not define behavior if user cancels file dialog
    if img_path:
        status_var.set(f"Selected: {Path(img_path).name}")

def convert_image():
    """Handle convert button click and execute the pipeline."""
    global img_path
    
    # FIXME: Spec does not define behavior if convert is clicked before opening an image
    if not img_path:
        status_var.set("Error: Please open an image first.")
        return
        
    out_path = Path(img_path).with_suffix(".docx")
    try:
        # FIXME: Spec assigns to a local variable `status` which won't update UI label; setting StringVar instead.
        status_var.set("Processing…")
        root.update()
        
        img    = preprocess(img_path)
        json_list = run_ocr(img)
        if not json_list:
            raise ValueError("No text detected in image or OCR failed.")
        paras  = format_blocks(json_list, img.width)
        export_docx(paras, str(out_path))
        status_var.set(f"Saved: {out_path.name}")
    except FileNotFoundError:
        status_var.set("Error: Tesseract not found. Check TESSERACT_CMD in config.py.")
    except Exception as e:
        status_var.set(f"Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Image-to-Word Converter MVP")
    
    status_var = tk.StringVar(value="Ready. Open an image.")
    
    open_btn = tk.Button(root, text="Open Image", command=open_image)
    open_btn.pack(pady=10)
    
    status_lbl = tk.Label(root, textvariable=status_var)
    status_lbl.pack(pady=10)
    
    convert_btn = tk.Button(root, text="Convert", command=convert_image)
    convert_btn.pack(pady=10)
    
    # TODO: Phase 2 - tables
    # TODO: Phase 2 - equations 
    # TODO: Phase 2 - multi-column 
    # TODO: Phase 2 - handwriting
    # TODO: Phase 2 - multi-page 
    # TODO: Phase 2 - multi-language
    
    root.mainloop()
