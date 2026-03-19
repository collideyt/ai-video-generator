import hashlib
import json
from pathlib import Path
from typing import List

from fastapi import UploadFile

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "outputs" / "uploads"
INDEX_PATH = UPLOAD_DIR / "index.json"


def ensure_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if not INDEX_PATH.exists():
        INDEX_PATH.write_text("{}", encoding="utf-8")
    return UPLOAD_DIR


def get_file_hash_bytes(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def get_file_hash(file_path: str | Path) -> str:
    with open(file_path, "rb") as handle:
        return hashlib.md5(handle.read()).hexdigest()


def _read_index() -> dict[str, str]:
    ensure_upload_dir()
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _write_index(index: dict[str, str]) -> None:
    INDEX_PATH.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _unique_destination(filename: str) -> Path:
    candidate = UPLOAD_DIR / filename
    if not candidate.exists():
        return candidate

    stem = candidate.stem
    suffix = candidate.suffix
    counter = 1
    while True:
        next_candidate = UPLOAD_DIR / f"{stem}_{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1


async def save_uploads(files: List[UploadFile]) -> List[str]:
    ensure_upload_dir()
    saved_paths: list[str] = []
    index = _read_index()

    for file in files:
        content = await file.read()
        file_hash = get_file_hash_bytes(content)
        existing_name = index.get(file_hash)

        if existing_name:
            existing_path = UPLOAD_DIR / existing_name
            if existing_path.exists():
                saved_paths.append(str(existing_path))
                continue

        destination = _unique_destination(file.filename or f"upload_{file_hash}")
        destination.write_bytes(content)
        index[file_hash] = destination.name
        saved_paths.append(str(destination))

    _write_index(index)
    return saved_paths
