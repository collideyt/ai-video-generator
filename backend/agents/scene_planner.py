TRANSITIONS = ["cut", "fade", "slide", "zoom"]


def plan_scenes(scenes: list[dict]) -> list[dict]:
    planned = []
    for idx, scene in enumerate(scenes):
        planned.append(
            {
                "scene_id": scene["scene"],
                "scene_text": scene["text"],
                "duration": scene["duration"],
                "visual_type": "product" if "product" in scene["text"].lower() else "broll",
                "transition": TRANSITIONS[idx % len(TRANSITIONS)],
            }
        )
    return planned
