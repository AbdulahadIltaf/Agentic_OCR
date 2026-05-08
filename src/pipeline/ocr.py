import json
import google.generativeai as genai
from config import GEMINI_MODEL

def run_ocr(img: "Image.Image") -> list:
    """PIL Image → extracted structured content via Gemini Vision API."""
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    prompt = """
    Extract all text and formatting from this image.
    Return ONLY a JSON array of objects with:
    "text": (string), "style": ("Heading 1" or "Normal"), "bold": (bool), "align": (0-left, 1-center, 2-right).
    No markdown wrappers.
    """
    
    try:
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Failed to process or parse Gemini response: {e}")
        return []
