# TraceDoc — Phase 2 (Agentic + PPIT)

Single-page **English document images** (JPG/PNG) → structured JSON (Gemini Vision) → **.docx**, with an **explainable agent loop**, **compliance sidebar** (JSON “RAG”), and **human-in-the-loop** export rules.

## Layout (Phase 2 only)

| Path | Role |
|------|------|
| `web/` | Static SPA (`index.html`, `style.css`, `script.js`) served by Flask |
| `src/app.py` | REST routes: `/api/agent/*`, `/api/compliance`, `/api/download/*` |
| `src/agent/` | `perceive`, `decide` (heuristics), `act`, `memory`, `compliance_db.json`, `xai_logs.json` |
| `src/pipeline/` | Preprocess + OCR (Gemini) + format + export |
| `slides/build_slides.py` | Builds `slides/TraceDoc_Phase2_Deck.pptx` (32 slides, guideline-aligned) |
| `TestSamples/` | PDFs for adversarial / normal demos |

## Prerequisites

- Python 3.10+ recommended  
- `GEMINI_API_KEY` in repo-root `API_KEYS/.env` (or export the variable). `src/config.py` searches `../API_KEYS/.env` relative to `implementation/`.

## Run

```powershell
cd path\to\Project\implementation
python -m venv virtvenv
.\virtvenv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\app.py
```

Browse **http://127.0.0.1:5000**.

### HITL rule (demo-friendly)

- **Confidence ≥ 80%:** export with one click.  
- **18% ≤ confidence < 80%:** UI checkbox + JSON field `acknowledge_risk: true` required; server returns 403 otherwise.  
- **Confidence < 18%** (structural abort): export disabled client- and server-side.

## Slides for your video / viva

```powershell
cd implementation
pip install python-pptx
python slides\build_slides.py
```

Output: `slides/TraceDoc_Phase2_Deck.pptx` — replace `[Your names]`, add screenshots of the new `web/` UI, and record the demo.

## Renaming / rebranding

Change visible strings in `web/index.html`, colors in `web/style.css`, and slide titles in `slides/build_slides.py`. Backend product name is not hardcoded in Python.
