import json
import uuid
from pathlib import Path
from agents.script_analyzer import split_script
from agents.scene_planner import plan_scenes
from agents.asset_matcher import match_assets
from agents.voiceover import generate_voiceover
from agents.captions import generate_captions
from video_engine.timeline_builder import build_timeline
from video_engine.ffmpeg_renderer import render_video

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = OUTPUTS_DIR / "uploads"


def generate_video(script: str, assets: list[str], logo: str | None, music: str | None, specs: dict) -> str:
    job_id = uuid.uuid4().hex
    print("Running video pipeline")
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if not assets:
        if UPLOADS_DIR.exists():
            assets = [str(p) for p in UPLOADS_DIR.iterdir() if p.is_file()]

    scenes = split_script(script, target_duration=specs.get("duration", 30))
    planned_scenes = plan_scenes(scenes)
    matched_scenes = match_assets(planned_scenes, assets)
    if assets and not any(scene.get("asset") for scene in matched_scenes):
        asset_cycle = [str(Path(p).resolve()) for p in assets]
        for idx, scene in enumerate(matched_scenes):
            scene["asset"] = asset_cycle[idx % len(asset_cycle)]

    voiceover_path = None
    if specs.get("voiceover", True):
        voiceover_path = generate_voiceover(script, job_id)

    captions_path = None
    if specs.get("captions", True):
        captions_path = generate_captions(script, job_id)

    timeline = build_timeline(matched_scenes, specs)
    timeline_path = output_dir / "timeline.json"
    with open(timeline_path, "w", encoding="utf-8") as handle:
        json.dump(timeline, handle, indent=2)

    render_video(
        timeline=timeline,
        assets=assets,
        voiceover=voiceover_path,
        captions=captions_path,
        logo=logo,
        music=music,
        job_id=job_id,
        specs=specs,
    )

    return f"/outputs/{job_id}/final_video.mp4"
