import asyncio
import json
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pipeline import generate_video
from utils.file_storage import save_uploads
from utils.job_status import (
    find_latest_render,
    initialize_job_status,
    read_job_status,
    update_job_status,
)

app = FastAPI(title="Collide AI Video Editor")

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Specs(BaseModel):
    duration: int = 30
    aspect_ratio: str = "9:16"
    captions: bool = True
    voiceover: bool = True


@app.post("/generate-video")
async def generate_video_endpoint(
    request: Request,
    prompt: Optional[str] = Form(None),
    style: Optional[str] = Form("cinematic"),
    voice: Optional[str] = Form("female"),
    duration: Optional[int] = Form(30),
    script: Optional[str] = Form(None),
    specs: Optional[str] = Form(None),
    images: Optional[List[UploadFile]] = File(None),
    videos: Optional[List[UploadFile]] = File(None),
    audio: Optional[UploadFile] = File(None),
    assets: Optional[List[UploadFile]] = File(None),
    logo: Optional[UploadFile] = File(None),
    music: Optional[UploadFile] = File(None),
):
    content_type = request.headers.get("content-type", "")
    is_json = "application/json" in content_type

    if is_json:
        data = await request.json()
        prompt = data.get("prompt")
        style = data.get("style", "cinematic")
        voice = data.get("voice", "female")
        duration = int(data.get("duration", 30))
        script = data.get("script")

    if not script and not prompt:
        raise HTTPException(status_code=400, detail="script or prompt is required")

    final_specs = {
        "duration": duration,
        "aspect_ratio": "16:9",
        "captions": True,
        "voiceover": (voice != "none"),
        "style": style,
        "voice": voice,
    }

    # If legacy specs JSON was provided, override generated ones
    if specs and not is_json:
        specs_obj = Specs(**json.loads(specs))
        final_specs.update(specs_obj.model_dump())

    import time
    start_time = time.time()
    job_id = uuid.uuid4().hex
    initialize_job_status(job_id)

    # Save uploads before returning so file handles are valid for the background task.
    saved_images, saved_videos, saved_audio, saved_legacy_assets, saved_logo, saved_music = await asyncio.gather(
        save_uploads(images or []),
        save_uploads(videos or []),
        save_uploads([audio] if audio else []),
        save_uploads(assets or []),
        save_uploads([logo] if logo else []),
        save_uploads([music] if music else []),
    )

    final_assets = {
        "images": saved_images + saved_legacy_assets,
        "videos": saved_videos,
        "audio": saved_audio[0] if saved_audio else None
    }

    logo_path = saved_logo[0] if saved_logo else None
    music_path = saved_music[0] if saved_music else None

    async def run_job() -> None:
        try:
            result = await asyncio.to_thread(
                generate_video,
                script=script,
                prompt=prompt,
                assets=final_assets,
                logo=logo_path,
                music=music_path,
                specs=final_specs,
                job_id=job_id,
            )
            time_taken = time.time() - start_time
            current = read_job_status(job_id) or {}
            current["time_taken"] = time_taken
            current["script"] = result.get("script", script)
            current["scenes"] = result.get("scenes", [])
            current["used_assets"] = result.get("used_assets", False)
            from utils.job_status import write_job_status
            write_job_status(job_id, current)
        except Exception as exc:
            current = read_job_status(job_id)
            update_job_status(
                job_id,
                overall_status="failed",
                completed_steps=[
                    step["label"]
                    for step in (current or {}).get("steps", [])
                    if step["state"] == "completed"
                ],
                current_step=(current or {}).get("current_step"),
                error=str(exc),
            )

    asyncio.create_task(run_job())
    
    return {
        "job_id": job_id,
        "status_url": f"/job-status/{job_id}",
        "video_url": None,
    }


@app.get("/job-status/{job_id}")
async def get_job_status(job_id: str):
    payload = read_job_status(job_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return payload


@app.get("/latest-render")
async def get_latest_render():
    return find_latest_render() or {"video_url": None, "job_status": None}


app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
