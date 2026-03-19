import json
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
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
    background_tasks: BackgroundTasks,
    script: str = Form(...),
    specs: str = Form(...),
    assets: Optional[List[UploadFile]] = File(None),
    logo: Optional[UploadFile] = File(None),
    music: Optional[UploadFile] = File(None),
):
    print("Received script:")
    print(script)
    specs_obj = Specs(**json.loads(specs))

    saved_assets = await save_uploads(assets or [])
    saved_logo = await save_uploads([logo] if logo else [])
    saved_music = await save_uploads([music] if music else [])

    job_id = uuid.uuid4().hex
    initialize_job_status(job_id)

    def run_job() -> None:
        try:
            generate_video(
                script=script,
                assets=saved_assets,
                logo=saved_logo[0] if saved_logo else None,
                music=saved_music[0] if saved_music else None,
                specs=specs_obj.model_dump(),
                job_id=job_id,
            )
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

    background_tasks.add_task(run_job)

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
