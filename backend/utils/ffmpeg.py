from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


def get_local_ffmpeg_path() -> Path:
    backend_dir = Path(__file__).resolve().parent.parent
    return (backend_dir / "ffmpeg" / "ffmpeg.exe").resolve()


def resolve_ffmpeg_path() -> Optional[str]:
    ffmpeg_path = get_local_ffmpeg_path()
    if ffmpeg_path.exists():
        return str(ffmpeg_path)
    return None
