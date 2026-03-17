from pathlib import Path
from typing import List
from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "outputs" / "uploads"


def ensure_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


async def save_uploads(files: List[UploadFile]) -> List[str]:
    ensure_upload_dir()
    saved_paths = []

    for file in files:
        destination = UPLOAD_DIR / file.filename
        content = await file.read()
        destination.write_bytes(content)
        saved_paths.append(str(destination))

    return saved_paths
