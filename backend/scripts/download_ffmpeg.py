import os
import shutil
import zipfile
from pathlib import Path

import requests

FFMPEG_ZIP_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def download_ffmpeg() -> Path:
    backend_dir = Path(__file__).resolve().parent.parent
    ffmpeg_dir = backend_dir / "ffmpeg"
    ffmpeg_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_exe = ffmpeg_dir / "ffmpeg.exe"

    if ffmpeg_exe.exists():
        return ffmpeg_exe

    temp_dir = ffmpeg_dir / "_tmp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    zip_path = temp_dir / "ffmpeg.zip"

    try:
        with requests.get(FFMPEG_ZIP_URL, stream=True, timeout=60) as response:
            response.raise_for_status()
            with open(zip_path, "wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)

        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(temp_dir)

        extracted_ffmpeg = None
        for root, _dirs, files in os.walk(temp_dir):
            if "ffmpeg.exe" in files:
                extracted_ffmpeg = Path(root) / "ffmpeg.exe"
                break

        if not extracted_ffmpeg:
            raise FileNotFoundError("ffmpeg.exe not found in archive")

        shutil.copy2(extracted_ffmpeg, ffmpeg_exe)
        return ffmpeg_exe
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    path = download_ffmpeg()
    print(f"FFmpeg ready at: {path}")
