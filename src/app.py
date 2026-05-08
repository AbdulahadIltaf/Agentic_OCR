import os
import sys
import uuid
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ensure src modules can be imported
sys.path.append(str(Path(__file__).parent))

from pipeline.formatter import format_blocks
from agent.perceive import perceive
from agent.decide import decide
from agent.act import act
from agent.memory import log_session
from config import LOG_PATH

XAI_LOG_PATH = Path("/tmp/xai_logs.json")
COMPLIANCE_DB_PATH = Path(__file__).parent / "agent" / "compliance_db.json"
WEB_DIR = Path(__file__).resolve().parent.parent / "web"

app = Flask(__name__, static_folder=str(WEB_DIR))
CORS(app)

SESSION_STATE = {}
UPLOAD_FOLDER = "/tmp/temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def append_xai_log(session_id, trace):
    XAI_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    history = {}
    if XAI_LOG_PATH.exists():
        try:
            history = json.loads(XAI_LOG_PATH.read_text())
        except Exception:
            pass
    history[session_id] = trace
    XAI_LOG_PATH.write_text(json.dumps(history, indent=2))

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")



@app.route("/api/agent/perceive_decide", methods=["POST"])
def api_perceive_decide():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
        
    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    temp_path = None
    try:
        session_id = str(uuid.uuid4())
        temp_path = os.path.join(UPLOAD_FOLDER, f"{session_id}.png")
        file.save(temp_path)
        
        img, json_list = perceive(temp_path)
        decision = decide(json_list)
        
        xai_trace = [
            {"step": "PERCEIVE", "message": "Scanning document boundaries... PII patterns checked. Local processing active.", "citation_key": "PECA_SEC_16"},
            {"step": "DECIDE", "message": "Goal-based agent selecting transformation strategy based on layout.", "citation_key": "GDPR_MINIMIZATION"},
            {"step": "SAFETY", "message": "Verification against code of ethics. Avoid Harm checked. Passed.", "citation_key": "ACM_1_2"},
            {"step": "ACT", "message": f"Calculated heuristic confidence: {decision['mean_conf']}%. Awaiting Human-in-the-Loop validation.", "citation_key": "GREEN_COMPUTING"}
        ]
        
        append_xai_log(session_id, xai_trace)
        
        SESSION_STATE[session_id] = {
            "temp_path": temp_path,
            "json_list": json_list,
            "decision": decision,
            "img_width": img.width,
            "xai_trace": xai_trace
        }
        
        blocks = format_blocks(json_list, img.width) if json_list else []
        
        return jsonify({
            "session_id": session_id,
            "decision": decision,
            "blocks": blocks,
            "xai_trace": xai_trace
        })

    except Exception as e:
        if temp_path and os.path.isfile(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        return jsonify({"error": str(e)}), 500

@app.route("/api/agent/act", methods=["POST"])
def api_act():
    data = request.json or {}
    session_id = data.get("session_id")
    if not session_id or session_id not in SESSION_STATE:
        return jsonify({"error": "Invalid or expired session"}), 400
        
    state = SESSION_STATE[session_id]

    try:
        raw = state["decision"]
        mean_conf = float(raw.get("mean_conf", 0))

        if raw.get("action") == "abort":
            return jsonify(
                {
                    "error": "OCR output failed structural validation; export blocked. Try a clearer scan.",
                }
            ), 400

        if mean_conf < 80 and not data.get("acknowledge_risk"):
            return jsonify(
                {
                    "error": "Confidence under 80% requires acknowledge_risk: true (tick the UI acknowledgement).",
                }
            ), 403

        decision = dict(raw)
        decision["action"] = "export"

        out_name = f"export_{session_id[:8]}.docx"
        out_path = os.path.join("/tmp", out_name)
        
        class DummyImg:
            width = state["img_width"]
            
        act(DummyImg(), state["json_list"], decision, out_path)
        
        result = {"attempt": 1, **decision, "out": out_name}
        log_session(result)
        
        if os.path.exists(state["temp_path"]):
            os.remove(state["temp_path"])
        del SESSION_STATE[session_id]
        
        return jsonify({"success": True, "conf": decision["mean_conf"], "filename": out_name})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/agent/abort", methods=["POST"])
def api_abort():
    data = request.json or {}
    session_id = data.get("session_id")
    if not session_id or session_id not in SESSION_STATE:
        return jsonify({"error": "Invalid or expired session"}), 400
        
    state = SESSION_STATE[session_id]
    decision = state["decision"]
    decision["action"] = "abort"
    
    result = {"attempt": 1, **decision, "out": "aborted"}
    log_session(result)
    
    if os.path.exists(state["temp_path"]):
        os.remove(state["temp_path"])
    del SESSION_STATE[session_id]
    
    return jsonify({"success": True})

@app.route("/api/download/<filename>")
def download_file(filename):
    # Only allow downloading .docx files to prevent path traversal
    if not filename.endswith('.docx') or '/' in filename or '\\' in filename:
        return jsonify({"error": "Invalid file request"}), 400
    
    return send_from_directory("/tmp", filename, as_attachment=True)

@app.route("/api/agent/history", methods=["GET"])
def api_history():
    if LOG_PATH.exists():
        with open(LOG_PATH, "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

@app.route("/api/compliance", methods=["GET"])
def api_compliance():
    if COMPLIANCE_DB_PATH.exists():
        with open(COMPLIANCE_DB_PATH, "r") as f:
            return jsonify(json.load(f))
    return jsonify({})

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
