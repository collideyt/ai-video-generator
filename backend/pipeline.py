import json
import uuid
import random
import subprocess
from pathlib import Path

from agents.asset_matcher import match_assets
from agents.captions import generate_captions
from agents.scene_planner import plan_scenes
from agents.script_analyzer import split_script
from agents.voiceover import generate_voiceover_for_scenes, fit_text_to_duration
from utils.job_status import update_job_status
from video_engine.ffmpeg_renderer import render_video
from video_engine.timeline_builder import build_timeline

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
UPLOADS_DIR = OUTPUTS_DIR / "uploads"
LEGACY_UPLOADS_DIR = BASE_DIR / "uploads"


def _generate_visual_for_scene(scene: dict, output_dir: Path, index: int) -> str:
    output_path = output_dir / f"ai_scene_{index}.mp4"
    ffmpeg_path = None
    try:
        import imageio_ffmpeg

        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        pass

    color = "#%06x" % random.randint(0, 0xFFFFFF)
    label = (scene.get("type") or "scene").upper()
    if ffmpeg_path:
        try:
            subprocess.run(
                [
                    ffmpeg_path,
                    "-y",
                    "-f",
                    "lavfi",
                    "-i",
                    f"color=c={color}:s=1080x1920:d={max(scene.get('duration', 5), 2)}",
                    "-vf",
                    f"drawtext=text='{label}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=h*0.45",
                    "-r",
                    "30",
                    "-an",
                    "-c:v",
                    "libx264",
                    "-pix_fmt",
                    "yuv420p",
                    str(output_path),
                ],
                check=True,
                capture_output=True,
            )
            return str(output_path)
        except Exception as exc:
            print(f"FFmpeg visual generation failed: {exc}")

    output_path.write_text(f"AI visual placeholder: {label}", encoding="utf-8")
    return str(output_path)


def generate_video(
    script: str | None = None,
    assets: dict | list | None = None,
    logo: str | None = None,
    music: str | None = None,
    specs: dict | None = None,
    job_id: str | None = None,
    prompt: str | None = None,
) -> dict:
    job_id = job_id or uuid.uuid4().hex
    specs = specs or {}
    render_id = uuid.uuid4().hex
    print("Running video pipeline")
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)

    completed_steps = []
    used_assets = False
    visual_assets = []
    audio_asset = None

    if isinstance(assets, dict):
        visual_assets = assets.get("images", []) + assets.get("videos", [])
        audio_asset = assets.get("audio")
        if visual_assets or audio_asset:
            used_assets = True
    elif isinstance(assets, list):
        visual_assets = assets
        if visual_assets:
            used_assets = True

    # Do not reuse old uploads implicitly
    if not visual_assets:
        visual_assets = []

    if prompt and not script:
        update_job_status(
            job_id,
            overall_status="processing",
            completed_steps=completed_steps,
            active_step="Generating script",
        )
        try:
            from agents.script_generator import generate_script_from_prompt

            script = generate_script_from_prompt(prompt, specs.get("style", "cinematic"), specs.get("duration", 30))
        except ImportError:
            script = json.dumps(
                {
                    "scenes": [
                        {"type": "hook", "text": f"Imagine {prompt}", "duration": 5},
                        {"type": "content", "text": f"We dive into {prompt}", "duration": 15},
                        {"type": "cta", "text": "Take action now.", "duration": 5},
                    ]
                }
            )
        completed_steps.append("Generating script")
    elif script:
        completed_steps.append("Generating script")

    if not script:
        script = ""

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=completed_steps,
        active_step="Analyzing script",
    )
    target_duration = float(specs.get("duration", 30))
    scenes = split_script(script, target_duration=target_duration)
    transition_gap = 0.5
    per_scene_duration = (target_duration + max(len(scenes) - 1, 0) * transition_gap) / max(len(scenes), 1)
    for scene in scenes:
        scene["duration"] = round(per_scene_duration, 2)
        narration = scene.get("raw_text") or scene.get("text") or ""
        narration = narration if isinstance(narration, str) else " ".join(narration)
        scene["raw_text"] = narration.strip()
        scene["text"] = [narration.strip()]
    print(f"Pipeline scenes count: {len(scenes)}")
    completed_steps.append("Analyzing script")

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=completed_steps,
        active_step="Planning scenes",
    )
    planned_scenes = plan_scenes(scenes)
    completed_steps.append("Planning scenes")

    update_job_status(
        job_id,
        overall_status="processing",
        completed_steps=completed_steps,
        active_step="Matching assets",
    )
    if visual_assets:
        matched_scenes = match_assets(planned_scenes, visual_assets)
    else:
        matched_scenes = []
        for idx, scene in enumerate(planned_scenes, start=1):
            scene_copy = dict(scene)
            scene_copy["asset"] = _generate_visual_for_scene(scene_copy, output_dir, idx)
            scene_copy["assets"] = [scene_copy["asset"]]
            matched_scenes.append(scene_copy)
    completed_steps.append("Matching assets")

    voiceover_concat = None
    voice_records = []
    if audio_asset:
        voiceover_concat = audio_asset
    elif specs.get("voiceover", True):
        update_job_status(
            job_id,
            overall_status="processing",
            completed_steps=completed_steps,
            active_step="Generating voiceover",
        )
        voice_records, voiceover_concat = generate_voiceover_for_scenes(
            matched_scenes, job_id, voice=specs.get("voice", "alloy"), transition_gap=transition_gap
        )
        for scene in matched_scenes:
            record = next((r for r in voice_records if r["scene"] == scene["scene_id"]), None)
            if record:
                scene["voice_path"] = record["path"]
        completed_steps.append("Generating voiceover")

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
        completed_steps=completed_steps,
        active_step="Rendering video",
    )

    music_path = music or (audio_asset if audio_asset and not voiceover_concat else None)

    final_video_name = f"final_video_{render_id}.mp4"
    video_path = render_video(
        timeline=timeline,
        assets=visual_assets,
        voiceover_records=voice_records if specs.get("voiceover", True) else [],
        captions=captions_path,
        logo=logo,
        music=music_path,
        job_id=job_id,
        specs=specs,
        output_filename=final_video_name,
    )
    completed_steps.append("Rendering video")

    video_url = f"/outputs/{job_id}/{final_video_name}"
    update_job_status(
        job_id,
        overall_status="completed",
        completed_steps=completed_steps,
        current_step="Rendering video",
        video_url=video_url,
    )

    return {
        "video_url": video_url,
        "script": script,
        "scenes": matched_scenes,
        "used_assets": used_assets,
        "duration": specs.get("duration", target_duration),
    }
