from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
from pipeline import generate_video
from utils.file_storage import save_uploads

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
    script: str = Form(...),
    specs: str = Form(...),
    assets: Optional[List[UploadFile]] = File(None),
    logo: Optional[UploadFile] = File(None),
    music: Optional[UploadFile] = File(None),
):
    specs_obj = Specs(**json.loads(specs))

    saved_assets = await save_uploads(assets or [])
    saved_logo = await save_uploads([logo] if logo else [])
    saved_music = await save_uploads([music] if music else [])

    result = generate_video(
        script=script,
        assets=saved_assets,
        logo=saved_logo[0] if saved_logo else None,
        music=saved_music[0] if saved_music else None,
        specs=specs_obj.model_dump(),
    )

    return {"video_url": result}


app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")
