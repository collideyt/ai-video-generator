import random
import re
from pathlib import Path

from utils.asset_loader import categorize_assets

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_UPLOAD_DIRS = [
    BASE_DIR / "uploads",
    BASE_DIR / "outputs" / "uploads",
]

HOOK_KEYWORDS = {"hook", "intro", "launch", "reveal", "dynamic", "fast"}
PROOF_KEYWORDS = {"proof", "testimonial", "changed", "evidence"}
INTERIOR_KEYWORDS = {"interior", "inside", "indoors", "lobby", "room", "suite"}
EXTERIOR_KEYWORDS = {"exterior", "outside", "outdoor", "street", "building", "hero"}
AERIAL_KEYWORDS = {"aerial", "drone", "dji", "birds-eye", "birdseye", "sky"}


def _normalized_asset_key(path: str) -> str:
    asset_path = Path(path)
    stem = re.sub(r"_\d+$", "", asset_path.stem.lower())
    stem = re.sub(r"\s+", " ", stem).strip()
    return f"{stem}{asset_path.suffix.lower()}"


def _load_asset_pool(assets: list[str]) -> list[str]:
    discovered = [str(Path(asset).resolve()) for asset in assets if Path(asset).is_file()]

    for directory in DEFAULT_UPLOAD_DIRS:
        if directory.exists():
            discovered.extend(str(path.resolve()) for path in directory.iterdir() if path.is_file())

    unique_assets: list[str] = []
    seen_keys: set[str] = set()
    for asset in dict.fromkeys(discovered):
        normalized = _normalized_asset_key(asset)
        if normalized in seen_keys:
            continue
        seen_keys.add(normalized)
        unique_assets.append(asset)

    categorized = categorize_assets(unique_assets)
    videos = categorized["videos"]
    images = categorized["images"]
    random.shuffle(videos)
    random.shuffle(images)
    return videos + images


def _filename_tokens(path: str) -> str:
    return Path(path).name.lower()


def get_asset(
    assets: list[str],
    all_assets: list[str],
    global_used_assets: set[str],
    scene_used_assets: set[str],
    previous_scene_assets: set[str],
) -> str | None:
    if not assets:
        assets = all_assets
    if not assets:
        return None

    for asset in assets:
        if asset not in global_used_assets and asset not in previous_scene_assets:
            global_used_assets.add(asset)
            scene_used_assets.add(asset)
            return asset

    for asset in assets:
        if asset not in global_used_assets:
            global_used_assets.add(asset)
            scene_used_assets.add(asset)
            return asset

    for asset in assets:
        if asset not in scene_used_assets and asset not in previous_scene_assets:
            scene_used_assets.add(asset)
            return asset

    for asset in assets:
        if asset not in scene_used_assets:
            scene_used_assets.add(asset)
            return asset

    for asset in all_assets:
        if asset not in global_used_assets and asset not in previous_scene_assets:
            global_used_assets.add(asset)
            scene_used_assets.add(asset)
            return asset

    for asset in all_assets:
        if asset not in global_used_assets:
            global_used_assets.add(asset)
            scene_used_assets.add(asset)
            return asset

    return random.choice(assets)


def _scene_candidates(scene: dict, all_assets: list[str]) -> tuple[list[str], list[str]]:
    categorized = categorize_assets(all_assets)
    videos = categorized["videos"]
    images = categorized["images"]

    scene_type = scene.get("type", "").lower()
    scene_text = scene.get("scene_text", "").lower()
    visual_hint = scene.get("visual_hint", "").lower()
    combined = f"{scene_type} {scene_text} {visual_hint}"

    aerial_videos = [asset for asset in videos if "dji" in _filename_tokens(asset)]
    interior_images = [asset for asset in images if "interior" in _filename_tokens(asset)]
    exterior_images = [asset for asset in images if "exterior" in _filename_tokens(asset)]
    hook_videos = [
        asset
        for asset in videos
        if any(keyword in _filename_tokens(asset) or keyword in combined for keyword in HOOK_KEYWORDS)
    ]

    primary: list[str] = []
    secondary: list[str] = []

    if scene_type == "hook":
        primary.extend(hook_videos or videos)
        secondary.extend(videos)
        secondary.extend(images)
    elif scene_type == "proof" or any(keyword in combined for keyword in PROOF_KEYWORDS):
        primary.extend(videos)
        secondary.extend(videos)
        secondary.extend(images)
    else:
        primary.extend(videos)
        secondary.extend(videos)
        secondary.extend(images)

    if any(keyword in combined for keyword in AERIAL_KEYWORDS):
        primary = aerial_videos or primary
    if any(keyword in combined for keyword in INTERIOR_KEYWORDS):
        secondary = interior_images or secondary
    if any(keyword in combined for keyword in EXTERIOR_KEYWORDS):
        secondary = exterior_images or secondary

    return primary, secondary


def _assets_per_scene(scene: dict, asset_pool: list[str]) -> int:
    duration = float(scene.get("duration", 3))
    scene_type = scene.get("type", "").lower()
    clip_duration_range = scene.get("clip_duration_range") or [0.8, 1.3]
    min_clip_duration = max(float(clip_duration_range[0]), 0.4)
    categorized = categorize_assets(asset_pool)
    videos = categorized["videos"]

    if len(asset_pool) <= 1:
        return 1
    if duration <= 1.5:
        return min(max(1, round(duration / min_clip_duration)), len(asset_pool), 3)

    if scene_type in {"hook", "problem", "shift"}:
        preferred = 4 if len(videos) >= 2 else 3
        return min(preferred, len(asset_pool))
    if scene_type in {"proof", "future", "cta"}:
        preferred = 3 if len(videos) >= 1 else 2
        return min(preferred, len(asset_pool))
    if duration >= 4 or len(videos) >= 2:
        return min(3, len(asset_pool))
    return min(2, len(asset_pool))


def match_assets(scenes: list[dict], assets: list[str]) -> list[dict]:
    asset_pool = _load_asset_pool(assets)
    matched = []
    global_used_assets: set[str] = set()
    previous_scene_assets: set[str] = set()

    for scene in scenes:
        scene_used_assets: set[str] = set()
        primary, secondary = _scene_candidates(scene, asset_pool)
        clip_count = _assets_per_scene(scene, asset_pool)

        selected_assets: list[str] = []
        last_type: str | None = None

        for clip_index in range(clip_count):
            candidate_pool = primary if clip_index == 0 else secondary
            if last_type == "image" and primary:
                candidate_pool = primary

            asset = get_asset(
                candidate_pool,
                asset_pool,
                global_used_assets,
                scene_used_assets,
                previous_scene_assets,
            )
            if asset is None:
                asset = get_asset(
                    asset_pool,
                    asset_pool,
                    global_used_assets,
                    scene_used_assets,
                    previous_scene_assets,
                )
            if asset is None:
                break

            selected_assets.append(asset)
            last_type = "video" if asset.lower().endswith((".mp4", ".mov", ".mkv", ".webm")) else "image"

        scene["assets"] = selected_assets
        scene["asset"] = selected_assets[0] if selected_assets else None
        matched.append(scene)
        previous_scene_assets = set(selected_assets)

    return matched
