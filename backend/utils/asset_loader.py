from pathlib import Path


def categorize_assets(paths: list[str]) -> dict:
    images = []
    videos = []

    for path in paths:
        ext = Path(path).suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".webp"}:
            images.append(path)
        elif ext in {".mp4", ".mov", ".mkv", ".webm"}:
            videos.append(path)

    return {"images": images, "videos": videos}
