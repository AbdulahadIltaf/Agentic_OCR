import json
import google.generativeai as genai
from config import GEMINI_MODEL

def run_ocr(img: "Image.Image") -> list:
    """PIL Image → extracted structured content via Gemini Vision API."""
    model = genai.GenerativeModel(GEMINI_MODEL)
    
    prompt = """
    Analyze the image. It contains notes, diagrams, and text.
    Extract all readable text in a logical flow. 
    Identify the formatting for each block of text.
    Return ONLY a valid JSON array of objects. Do not include markdown wrappers (like ```json).
    Each object must have these keys:
    "text": (string) The extracted text for a paragraph or line
    "style": (string) "Heading 1" for big titles, or "Normal" for regular text
    "bold": (boolean) true if the text looks bold, false otherwise
    "align": (integer) 0 for left, 1 for center, 2 for right
    
    Do your best to transcribe any diagrams as descriptive text or just extract their labels sequentially.
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
