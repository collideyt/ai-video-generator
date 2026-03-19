TRANSITIONS = ["cut", "fade", "slide", "zoom"]


def plan_scenes(scenes: list[dict]) -> list[dict]:
    planned = []

    for idx, scene in enumerate(scenes):
        scene_type = scene.get("scene_type", "content")
        scene_text_lines = scene.get("text") or [scene.get("raw_text", "")]
        scene_text = " ".join(scene_text_lines).strip()
        transition = scene.get("transition") or TRANSITIONS[idx % len(TRANSITIONS)]

        edit_style = "standard"
        visual_type = "broll"
        text_overlay = "default"

        if scene_type == "hook":
            edit_style = "fast-cuts"
            visual_type = "high-energy"
            text_overlay = "kinetic"
        elif scene_type == "problem":
            edit_style = "contrast-visuals"
            visual_type = "contrast"
            text_overlay = "emphasis"
        elif scene_type == "cta":
            edit_style = "conversion-push"
            visual_type = "brand"
            text_overlay = "strong"
        elif scene_type == "demo":
            edit_style = "feature-walkthrough"
            visual_type = "product"

        planned.append(
            {
                "scene_id": scene["scene"],
                "scene_text": scene_text,
                "text": scene_text_lines,
                "duration": scene["duration"],
                "type": scene_type,
                "visual_type": visual_type,
                "visual_hint": scene.get("visual_hint", ""),
                "transition": transition,
                "style": scene.get("style", "default"),
                "edit_style": edit_style,
                "text_overlay": text_overlay,
                "start": scene.get("start"),
                "end": scene.get("end"),
            }
        )

    return planned
