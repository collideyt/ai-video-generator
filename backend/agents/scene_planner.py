TRANSITIONS = ["cut", "slide", "zoom", "fade"]

SCENE_PRESETS = {
    "hook": {
        "pace": "fast",
        "text_animation": "slide_up",
        "motion_style": "zoom_in",
        "motion_profile": "aggressive",
        "motion_intensity": "high",
        "subclip_motion_cycle": ["zoom_in", "pan_left", "zoom_in", "pan_right"],
        "text_layout": "center_focus",
        "clip_duration_range": [0.5, 1.0],
        "transition_pool": ["cut", "zoom", "cut", "slide"],
        "edit_style": "fast-cuts",
        "visual_type": "high-energy",
        "text_overlay": "kinetic",
    },
    "problem": {
        "pace": "fast",
        "text_animation": "fade_in",
        "motion_style": "drift",
        "motion_profile": "restrained",
        "motion_intensity": "low",
        "subclip_motion_cycle": ["drift", "pan_left", "drift"],
        "text_layout": "bold_center",
        "clip_duration_range": [0.7, 1.1],
        "transition_pool": ["cut", "fade", "cut"],
        "edit_style": "contrast-visuals",
        "visual_type": "contrast",
        "text_overlay": "emphasis",
    },
    "shift": {
        "pace": "fast",
        "text_animation": "slide_up",
        "motion_style": "zoom_in",
        "motion_profile": "transition-led",
        "motion_intensity": "medium",
        "subclip_motion_cycle": ["zoom_in", "zoom_out", "pan_right"],
        "text_layout": "center_focus",
        "clip_duration_range": [0.6, 1.0],
        "transition_pool": ["zoom", "cut", "zoom"],
        "edit_style": "pivot-transition",
        "visual_type": "momentum",
        "text_overlay": "kinetic",
    },
    "proof": {
        "pace": "slow",
        "text_animation": "fade_in",
        "motion_style": "pan_right",
        "motion_profile": "cinematic",
        "motion_intensity": "low",
        "subclip_motion_cycle": ["pan_right", "pan_left", "drift"],
        "text_layout": "center_stack",
        "clip_duration_range": [1.0, 1.5],
        "transition_pool": ["fade", "slide", "fade"],
        "edit_style": "trust-build",
        "visual_type": "broll",
        "text_overlay": "supporting",
    },
    "cta": {
        "pace": "medium",
        "text_animation": "scale_in",
        "motion_style": "push_in",
        "motion_profile": "conversion",
        "motion_intensity": "medium",
        "subclip_motion_cycle": ["push_in", "drift", "zoom_in"],
        "text_layout": "center_focus",
        "clip_duration_range": [0.9, 1.3],
        "transition_pool": ["zoom", "cut", "fade"],
        "edit_style": "conversion-push",
        "visual_type": "brand",
        "text_overlay": "strong",
    },
    "future": {
        "pace": "medium",
        "text_animation": "fade_in",
        "motion_style": "pan_left",
        "motion_profile": "cinematic",
        "motion_intensity": "medium",
        "subclip_motion_cycle": ["pan_left", "push_in", "drift"],
        "text_layout": "center_stack",
        "clip_duration_range": [0.8, 1.3],
        "transition_pool": ["slide", "zoom", "fade"],
        "edit_style": "aspirational",
        "visual_type": "broll",
        "text_overlay": "default",
    },
    "demo": {
        "pace": "medium",
        "text_animation": "slide_up",
        "motion_style": "pan_up",
        "motion_profile": "guided",
        "motion_intensity": "medium",
        "subclip_motion_cycle": ["pan_up", "pan_right", "push_in"],
        "text_layout": "center_stack",
        "clip_duration_range": [0.8, 1.2],
        "transition_pool": ["slide", "cut", "zoom"],
        "edit_style": "feature-walkthrough",
        "visual_type": "product",
        "text_overlay": "default",
    },
    "content": {
        "pace": "medium",
        "text_animation": "fade_in",
        "motion_style": "push_in",
        "motion_profile": "steady",
        "motion_intensity": "medium",
        "subclip_motion_cycle": ["push_in", "pan_right", "drift"],
        "text_layout": "center_stack",
        "clip_duration_range": [0.8, 1.3],
        "transition_pool": ["cut", "slide", "fade"],
        "edit_style": "standard",
        "visual_type": "broll",
        "text_overlay": "default",
    },
}


def plan_scenes(scenes: list[dict]) -> list[dict]:
    planned = []

    for idx, scene in enumerate(scenes):
        scene_type = scene.get("scene_type", "content")
        scene_text_lines = scene.get("text") or [scene.get("raw_text", "")]
        scene_text = " ".join(scene_text_lines).strip()
        preset = SCENE_PRESETS.get(scene_type, SCENE_PRESETS["content"])
        transition_pool = preset.get("transition_pool", TRANSITIONS)
        transition = scene.get("transition") or transition_pool[idx % len(transition_pool)]

        planned.append(
            {
                "scene_id": scene["scene"],
                "scene_text": scene_text,
                "text": scene_text_lines,
                "duration": scene["duration"],
                "type": scene_type,
                "scene_preset": scene_type,
                "visual_type": preset.get("visual_type", "broll"),
                "visual_hint": scene.get("visual_hint", ""),
                "transition": transition,
                "style": scene.get("style", "default"),
                "edit_style": preset.get("edit_style", "standard"),
                "text_overlay": preset.get("text_overlay", "default"),
                "pace": preset.get("pace", "medium"),
                "text_animation": preset.get("text_animation", "fade_in"),
                "motion_style": preset.get("motion_style", "push_in"),
                "motion_profile": preset.get("motion_profile", "steady"),
                "motion_intensity": preset.get("motion_intensity", "medium"),
                "subclip_motion_cycle": preset.get("subclip_motion_cycle", ["push_in"]),
                "text_layout": preset.get("text_layout", "center_stack"),
                "clip_duration_range": preset.get("clip_duration_range", [0.8, 1.3]),
                "transition_pool": transition_pool,
                "start": scene.get("start"),
                "end": scene.get("end"),
            }
        )

    return planned
