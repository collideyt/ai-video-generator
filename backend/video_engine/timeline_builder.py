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
                "assets": scene.get("assets", [scene.get("asset")] if scene.get("asset") else []),
                "text": scene.get("text", [scene["scene_text"]]),
                "scene_text": scene["scene_text"],
                "type": scene.get("type", "content"),
                "visual": scene.get("visual_hint", ""),
                "transition": scene.get("transition", "cut"),
                "style": scene.get("style", "default"),
                "edit_style": scene.get("edit_style", "standard"),
                "scene_preset": scene.get("scene_preset", scene.get("type", "content")),
                "text_overlay": scene.get("text_overlay", "default"),
                "pace": scene.get("pace", "medium"),
                "text_animation": scene.get("text_animation", "fade_in"),
                "motion_style": scene.get("motion_style", "push_in"),
                "motion_profile": scene.get("motion_profile", "steady"),
                "motion_intensity": scene.get("motion_intensity", "medium"),
                "subclip_motion_cycle": scene.get("subclip_motion_cycle", [scene.get("motion_style", "push_in")]),
                "text_layout": scene.get("text_layout", "center_stack"),
                "clip_duration_range": scene.get("clip_duration_range", [0.8, 1.3]),
                "transition_pool": scene.get("transition_pool", [scene.get("transition", "cut")]),
            }
        )

    return {
        "specs": specs,
        "timeline": timeline,
    }
