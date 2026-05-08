import cv2
from PIL import Image

def preprocess(path: str) -> Image.Image:
    """Load image at path → binarized PIL Image for OCR."""
    img  = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return Image.fromarray(gray)
