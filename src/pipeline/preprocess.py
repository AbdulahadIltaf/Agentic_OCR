from PIL import Image

def preprocess(path: str) -> Image.Image:
    """Load image at path → binarized PIL Image for OCR."""
    img = Image.open(path)
    return img.convert("L")
