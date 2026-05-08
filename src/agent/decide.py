"""Heuristic confidence from structured OCR JSON (Gemini or any compatible source)."""

INJECTION_HINTS = (
    "ignore previous",
    "ignore all prior",
    "system prompt",
    "you are now",
    "disregard the",
    "new instructions:",
    "override your",
)


def _block_score(item: object) -> float:
    if not isinstance(item, dict):
        return 0.0

    text = item.get("text")
    t = (text if isinstance(text, str) else "").strip()
    blob = t.lower()

    for hint in INJECTION_HINTS:
        if hint in blob:
            return 4.0

    score = 0.0
    if len(t) > 0:
        score += min(42.0, 12.0 + min(len(t), 800) / 800.0 * 30.0)

    if isinstance(item.get("style"), str) and item["style"].strip():
        score += 20.0
    if isinstance(item.get("bold"), bool):
        score += 12.0
    if isinstance(item.get("align"), (int, float)) or item.get("align") in (0, 1, 2, 3):
        score += 14.0

    return min(100.0, score)


def decide(json_list: list) -> dict:
    """
    Returns mean_conf in [0,100], retry hint for CLI loops, and action for act().
    Empty or near-empty structure → abort so act() does not silently ship garbage.
    """
    if not json_list:
        return {"action": "abort", "mean_conf": 0.0, "retry": True}

    scores = [_block_score(x) for x in json_list]
    mean_conf = round(sum(scores) / len(scores), 2)
    retry = mean_conf < 52.0
    action = "export" if mean_conf >= 18.0 else "abort"
    return {"action": action, "mean_conf": mean_conf, "retry": retry}
