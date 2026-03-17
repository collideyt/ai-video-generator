from pathlib import Path


def generate_captions(script: str, job_id: str) -> str:
    output_dir = Path("outputs") / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "captions.srt"

    try:
        import whisper

        # Placeholder: if a future audio file is present, run whisper here.
        # For now, create a simple SRT from script sentences.
        raise RuntimeError("Use placeholder")
    except Exception:
        sentences = [s.strip() for s in script.split(".") if s.strip()]
        lines = []
        timestamp = 0
        for idx, sentence in enumerate(sentences, start=1):
            start = _format_time(timestamp)
            end = _format_time(timestamp + 3)
            lines.append(f"{idx}\n{start} --> {end}\n{sentence}\n")
            timestamp += 3
        output_path.write_text("\n".join(lines), encoding="utf-8")

    return str(output_path)


def _format_time(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"
