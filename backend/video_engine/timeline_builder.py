def _normalize_timeline_duration(timeline: list[dict], target_duration: float, tolerance: float = 2.0) -> list[dict]:
    """
    Scale and clamp scene durations so the total runtime stays close to the requested duration.
    If the total is already within tolerance, the original timeline is returned unchanged.
    """
    total_duration = sum(float(scene.get("duration", 0)) for scene in timeline)
    if not total_duration or abs(total_duration - target_duration) <= tolerance:
        return timeline

    scale = target_duration / total_duration
    adjusted: list[dict] = []
    elapsed = 0.0

    for index, scene in enumerate(timeline):
        base_duration = float(scene.get("duration", 0))
        if index == len(timeline) - 1:
            duration = max(0.5, round(target_duration - elapsed, 2))
        else:
            duration = max(0.5, round(base_duration * scale, 2))

        start = round(elapsed, 2)
        end = round(start + duration, 2)
        elapsed = end

        adjusted.append(
            {
                **scene,
                "start": start,
                "end": end,
                "duration": duration,
            }
        )

    return adjusted


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
                "voice": scene.get("voice_path"),
            }
        )

    target_duration = float(specs.get("duration", 30))
    normalized_timeline = _normalize_timeline_duration(timeline, target_duration)

    return {
        "specs": specs,
        "timeline": normalized_timeline,
    }
