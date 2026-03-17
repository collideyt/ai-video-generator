from utils.asset_loader import categorize_assets

CTA_KEYWORDS = {"get started", "sign up", "try", "cta", "call to action"}
DEMO_KEYWORDS = {"demo", "workflow", "product", "platform"}


def match_assets(scenes: list[dict], assets: list[str]) -> list[dict]:
    categorized = categorize_assets(assets)
    image_assets = categorized["images"]
    video_assets = categorized["videos"]

    matched = []
    image_idx = 0
    video_idx = 0

    for scene in scenes:
        text = scene["scene_text"].lower()
        asset = None

        if any(keyword in text for keyword in CTA_KEYWORDS):
            asset = image_assets[0] if image_assets else None
        elif any(keyword in text for keyword in DEMO_KEYWORDS):
            asset = video_assets[video_idx] if video_assets else None
            video_idx = (video_idx + 1) % max(1, len(video_assets))
        else:
            asset = image_assets[image_idx] if image_assets else None
            image_idx = (image_idx + 1) % max(1, len(image_assets))

        scene["asset"] = asset
        matched.append(scene)

    return matched
