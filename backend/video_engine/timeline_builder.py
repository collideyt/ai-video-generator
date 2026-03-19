def build_timeline(scenes: list[dict], specs: dict) -> dict:
    timeline = []
    for scene in scenes:
        start = scene.get("start", 0)
        end = scene.get("end", start + scene["duration"])

        timeline.append(
            {
                "start": start,
                "end": end,
                "duration": scene["duration"],
                "asset": scene.get("asset"),
                "text": scene.get("text", [scene["scene_text"]]),
                "scene_text": scene["scene_text"],
                "type": scene.get("type", "content"),
                "visual": scene.get("visual_hint", ""),
                "transition": scene.get("transition", "cut"),
                "style": scene.get("style", "default"),
                "edit_style": scene.get("edit_style", "standard"),
                "text_overlay": scene.get("text_overlay", "default"),
            }
        )

    return {
        "specs": specs,
        "timeline": timeline,
    }
