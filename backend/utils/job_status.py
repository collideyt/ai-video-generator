import json
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

PIPELINE_STEPS = [
    "Analyzing script",
    "Planning scenes",
    "Matching assets",
    "Generating voiceover",
    "Rendering video",
]


def _status_path(job_id: str) -> Path:
    job_dir = OUTPUTS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    return job_dir / "status.json"


def initialize_job_status(job_id: str) -> dict:
    payload = {
        "job_id": job_id,
        "status": "queued",
        "current_step": PIPELINE_STEPS[0],
        "steps": [{"label": step, "state": "pending"} for step in PIPELINE_STEPS],
        "video_url": None,
        "error": None,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    return write_job_status(job_id, payload)


def read_job_status(job_id: str) -> dict | None:
    path = _status_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_job_status(job_id: str, payload: dict) -> dict:
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()
    _status_path(job_id).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def update_job_status(
    job_id: str,
    *,
    overall_status: str,
    completed_steps: list[str],
    active_step: str | None = None,
    current_step: str | None = None,
    video_url: str | None = None,
    error: str | None = None,
) -> dict:
    payload = read_job_status(job_id) or initialize_job_status(job_id)
    payload["status"] = overall_status
    payload["current_step"] = current_step or active_step or payload.get("current_step")
    payload["steps"] = [
        {
            "label": step,
            "state": "completed"
            if step in completed_steps
            else "active"
            if step == active_step
            else "pending",
        }
        for step in PIPELINE_STEPS
    ]
    if video_url is not None:
        payload["video_url"] = video_url
    if error is not None:
        payload["error"] = error
    return write_job_status(job_id, payload)


def find_latest_render() -> dict | None:
    if not OUTPUTS_DIR.exists():
        return None

    latest: tuple[float, dict] | None = None
    for directory in OUTPUTS_DIR.iterdir():
        if not directory.is_dir() or directory.name == "uploads":
            continue

        final_video = directory / "final_video.mp4"
        if not final_video.exists():
            continue

        payload = {
            "job_id": directory.name,
            "video_url": f"/outputs/{directory.name}/final_video.mp4",
            "updated_at": datetime.fromtimestamp(final_video.stat().st_mtime, timezone.utc).isoformat(),
            "job_status": read_job_status(directory.name),
        }
        timestamp = final_video.stat().st_mtime
        if latest is None or timestamp > latest[0]:
            latest = (timestamp, payload)

    return latest[1] if latest else None
