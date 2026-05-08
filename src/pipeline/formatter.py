def format_blocks(json_list: list, img_w: int = 0) -> list:
    """Pass-through structured content from Gemini to the exporter format."""
    out = []
    for block in json_list:
        if not isinstance(block, dict) or "text" not in block:
            continue
        out.append({
            "text" : block.get("text", ""),
            "style": block.get("style", "Normal"),
            "bold" : bool(block.get("bold", False)),
            "align": int(block.get("align", 0)) # 0: LEFT, 1: CENTER, 2: RIGHT
        })
    return out
