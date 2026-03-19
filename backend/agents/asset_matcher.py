import random
from pathlib import Path
import math

from utils.asset_loader import categorize_assets

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_UPLOAD_DIRS = [
    BASE_DIR / "uploads",
    BASE_DIR / "outputs" / "uploads",
]

HOOK_KEYWORDS = {"hook", "intro", "launch", "reveal", "dynamic", "fast"}
INTERIOR_KEYWORDS = {"interior", "inside", "indoors", "lobby", "room", "suite"}
EXTERIOR_KEYWORDS = {"exterior", "outside", "outdoor", "street", "building", "hero"}
AERIAL_KEYWORDS = {"aerial", "drone", "dji", "birds-eye", "birdseye", "sky"}


def _load_asset_pool(assets: list[str]) -> list[str]:
    discovered = [str(Path(asset).resolve()) for asset in assets if Path(asset).is_file()]

    for directory in DEFAULT_UPLOAD_DIRS:
        if directory.exists():
            discovered.extend(str(path.resolve()) for path in directory.iterdir() if path.is_file())

    categorized = categorize_assets(list(dict.fromkeys(discovered)))
    unique_assets = categorized["videos"] + categorized["images"]
    random.shuffle(unique_assets)
    return unique_assets


def _filename_tokens(path: str) -> str:
    return Path(path).name.lower()


def _pick_from_candidates(
    candidates: list[str],
    usage_count: dict[str, int],
    used_assets: set[str],
) -> str | None:
    if not candidates:
        return None

    shuffled = candidates[:]
    random.shuffle(shuffled)
    available = [asset for asset in shuffled if asset not in used_assets]
    pool = available or shuffled
    return min(pool, key=lambda asset: (usage_count.get(asset, 0), _filename_tokens(asset)))


def _pick_scene_asset(
    scene: dict,
    all_assets: list[str],
    usage_count: dict[str, int],
    used_assets: set[str],
    force_unused: bool,
) -> str | None:
    if not all_assets:
        return None

    categorized = categorize_assets(all_assets)
    video_assets = categorized["videos"]
    image_assets = categorized["images"]

    scene_type = scene.get("type", "").lower()
    scene_text = scene.get("scene_text", "").lower()
    visual_hint = scene.get("visual_hint", "").lower()
    combined_text = f"{scene_type} {scene_text} {visual_hint}"

    aerial_candidates = [asset for asset in all_assets if "dji" in _filename_tokens(asset)]
    interior_candidates = [asset for asset in all_assets if "interior" in _filename_tokens(asset)]
    exterior_candidates = [asset for asset in all_assets if "exterior" in _filename_tokens(asset)]
    hook_candidates = [
        asset
        for asset in (video_assets or all_assets)
        if any(keyword in _filename_tokens(asset) or keyword in combined_text for keyword in HOOK_KEYWORDS)
    ]

    if scene_type == "hook":
        candidates = hook_candidates or video_assets or all_assets
        if force_unused:
            candidates = [asset for asset in candidates if asset not in used_assets] or candidates
        return _pick_from_candidates(candidates, usage_count, used_assets)
    if any(keyword in combined_text for keyword in AERIAL_KEYWORDS):
        candidates = aerial_candidates or video_assets or all_assets
        if force_unused:
            candidates = [asset for asset in candidates if asset not in used_assets] or candidates
        return _pick_from_candidates(candidates, usage_count, used_assets)
    if any(keyword in combined_text for keyword in INTERIOR_KEYWORDS):
        candidates = interior_candidates or image_assets or all_assets
        if force_unused:
            candidates = [asset for asset in candidates if asset not in used_assets] or candidates
        return _pick_from_candidates(candidates, usage_count, used_assets)
    if any(keyword in combined_text for keyword in EXTERIOR_KEYWORDS):
        candidates = exterior_candidates or image_assets or all_assets
        if force_unused:
            candidates = [asset for asset in candidates if asset not in used_assets] or candidates
        return _pick_from_candidates(candidates, usage_count, used_assets)

    remaining = [asset for asset in all_assets if asset not in used_assets]
    fallback_pool = remaining if force_unused and remaining else remaining or all_assets
    random.shuffle(fallback_pool)
    return min(fallback_pool, key=lambda asset: (usage_count.get(asset, 0), _filename_tokens(asset)))


def match_assets(scenes: list[dict], assets: list[str]) -> list[dict]:
    asset_pool = _load_asset_pool(assets)
    usage_count: dict[str, int] = {}
    used_assets: set[str] = set()
    matched = []
    target_unique_assets = (
        min(len(scenes), math.ceil(len(asset_pool) * 0.8))
        if len(asset_pool) > 5
        else min(len(scenes), len(asset_pool))
    )

    for scene in scenes:
        force_unused = len(used_assets) < target_unique_assets
        asset = _pick_scene_asset(scene, asset_pool, usage_count, used_assets, force_unused)
        if asset:
            usage_count[asset] = usage_count.get(asset, 0) + 1
            used_assets.add(asset)
        scene["asset"] = asset
        matched.append(scene)

    return matched
