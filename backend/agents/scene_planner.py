TRANSITIONS = ["cut", "fade", "slide", "zoom"]


def plan_scenes(scenes: list[dict]) -> list[dict]:
    planned = []
    total = len(scenes)
    for idx, scene in enumerate(scenes):
        if idx == 0:
            scene_type = "hook"
        elif idx == total - 1:
            scene_type = "cta"
        else:
            scene_type = "content"
        planned.append(
            {
                "scene_id": scene["scene"],
                "scene_text": scene["text"],
                "duration": scene["duration"],
                "type": scene_type,
                "visual_type": "product" if "product" in scene["text"].lower() else "broll",
                "transition": TRANSITIONS[idx % len(TRANSITIONS)],
            }
        )
    return planned
