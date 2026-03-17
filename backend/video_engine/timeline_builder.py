from itertools import accumulate


def build_timeline(scenes: list[dict], specs: dict) -> dict:
    durations = [scene["duration"] for scene in scenes]
    starts = [0] + list(accumulate(durations))[:-1]

    timeline = []
    for scene, start in zip(scenes, starts):
        timeline.append(
            {
                "start": start,
                "duration": scene["duration"],
                "asset": scene.get("asset"),
                "text": scene["scene_text"],
                "transition": scene.get("transition", "cut"),
            }
        )

    return {
        "specs": specs,
        "timeline": timeline,
    }
