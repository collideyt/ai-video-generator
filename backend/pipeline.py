import json
import uuid
from pathlib import Path

from agents.asset_matcher import match_assets
from agents.captions import generate_captions
from agents.scene_planner import plan_scenes
from agents.script_analyzer import split_script
from agents.voiceover import generate_voiceover
from utils.job_status import update_job_status
from video_engine.ffmpeg_renderer import render_video
from video_engine.timeline_builder import build_timeline

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = OUTPUTS_DIR / "uploads"
LEGACY_UPLOADS_DIR = BASE_DIR / "uploads"


def generate_video(
    script: str,
    assets: list[str],
    logo: str | None,
    music: str | None,
    specs: dict,
    job_id: str | None = None,
) -> str:
    job_id = job_id or uuid.uuid4().hex
    print("Running video pipeline")
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    if not assets:
        sources = []
        if UPLOADS_DIR.exists():
            sources.append(UPLOADS_DIR)
        if LEGACY_UPLOADS_DIR.exists():
            sources.append(LEGACY_UPLOADS_DIR)
        assets = [str(p) for src in sources for p in src.iterdir() if p.is_file()]

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=[],
        active_step="Analyzing script",
    )
    scenes = split_script(script, target_duration=specs.get("duration", 30))
    print(f"Pipeline scenes count: {len(scenes)}")

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=["Analyzing script"],
        active_step="Planning scenes",
    )
    planned_scenes = plan_scenes(scenes)

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=["Analyzing script", "Planning scenes"],
        active_step="Matching assets",
    )
    matched_scenes = match_assets(planned_scenes, assets)

    voiceover_path = None
    if specs.get("voiceover", True):
        update_job_status(
            job_id,
            overall_status="processing",
            completed_steps=["Analyzing script", "Planning scenes", "Matching assets"],
            active_step="Generating voiceover",
        )
        voiceover_path = generate_voiceover(script, job_id)

    captions_path = None
    if specs.get("captions", True):
        captions_path = generate_captions(script, job_id)

    timeline = build_timeline(matched_scenes, specs)
    timeline_path = output_dir / "timeline.json"
    with open(timeline_path, "w", encoding="utf-8") as handle:
        json.dump(timeline, handle, indent=2)

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=[
            "Analyzing script",
            "Planning scenes",
            "Matching assets",
            "Generating voiceover",
        ],
        active_step="Rendering video",
    )
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

    video_url = f"/outputs/{job_id}/final_video.mp4"
    update_job_status(
        job_id,
        overall_status="completed",
        completed_steps=[
            "Analyzing script",
            "Planning scenes",
            "Matching assets",
            "Generating voiceover",
            "Rendering video",
        ],
        current_step="Rendering video",
        video_url=video_url,
    )

    return video_url
