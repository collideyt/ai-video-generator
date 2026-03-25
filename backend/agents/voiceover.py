import os
import subprocess
from pathlib import Path
from typing import Iterable, List, Tuple

import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def _ensure_dir(job_id: str) -> Path:
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def _audio_duration(path: Path) -> float:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    try:
        result = subprocess.run(
            [ffmpeg_path, "-i", str(path)], capture_output=True, text=True, check=False
        )
        stderr = result.stderr or ""
        for line in stderr.splitlines():
            if "Duration" in line:
                parts = line.strip().split("Duration:")
                if len(parts) < 2:
                    continue
                timestamp = parts[1].split(",")[0].strip()
                h, m, s = timestamp.split(":")
                return round(float(h) * 3600 + float(m) * 60 + float(s), 2)
    except Exception:
        pass
    return 0.0


def _openai_tts(text: str, output_path: Path, voice: str) -> bool:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice or "alloy",
            input=text,
        )
        response.stream_to_file(str(output_path))
        return True
    except Exception as exc:
        print(f"OpenAI TTS failed: {exc}")
        return False


def _edge_tts(text: str, output_path: Path, voice: str) -> bool:
    try:
        import edge_tts
    except Exception:
        return False

    try:
        communicate = edge_tts.Communicate(text, voice or "en-US-JennyNeural")
        with open(output_path, "wb") as f:
            for chunk in communicate.stream_sync():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        return True
    except Exception as exc:
        print(f"edge-tts failed: {exc}")
        return False


def _gtts_fallback(text: str, output_path: Path) -> bool:
    try:
        from gtts import gTTS

        gTTS(text=text, lang="en", slow=False).save(str(output_path))
        return True
    except Exception as exc:
        print(f"gTTS failed: {exc}")
        return False


def _synthesize(text: str, target: Path, voice: str) -> bool:
    voice_resolved = voice
    if voice and voice.lower() == "female":
        voice_resolved = "en-US-JennyNeural"
    elif voice and voice.lower() == "male":
        voice_resolved = "en-US-GuyNeural"
    return _openai_tts(text, target, voice_resolved) or _edge_tts(text, target, voice_resolved) or _gtts_fallback(text, target)


def fit_text_to_duration(text: str, duration_sec: float, words_per_minute: int = 150) -> str:
    if duration_sec <= 0:
        return ""
    words = text.split()
    max_words = max(4, int(words_per_minute * (duration_sec / 60.0)))
    if len(words) <= max_words:
        return " ".join(words)
    trimmed = words[:max_words - 1]
    return " ".join(trimmed + ["..."])


def clean_voice_text(text: str) -> str:
    cleaned = text.replace("Hook:", "").replace("Scene:", "").replace("Content:", "")
    cleaned = cleaned.replace("{", " ").replace("}", " ").replace("[", " ").replace("]", " ")
    for token in ["div", "span", "script", "json", "type", "duration", "text"]:
        cleaned = cleaned.replace(token + ":", " ")
    # strip html tags
    import re
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\\s+", " ", cleaned).strip()
    return cleaned


def _pad_audio_to_duration(src: Path, dst: Path, duration: float) -> None:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i",
            str(src),
            "-af",
            f"apad=pad_dur={max(duration,0.1)},atrim=duration={max(duration,0.1)}",
            str(dst),
        ],
        check=True,
        capture_output=True,
    )


def generate_voiceover_for_scenes(
    scenes: Iterable[dict], job_id: str, voice: str | None = None, transition_gap: float = 0.5
) -> Tuple[List[dict], str | None]:
    output_dir = _ensure_dir(job_id)
    voice_records: List[dict] = []

    for idx, scene in enumerate(scenes, start=1):
        raw = " ".join(scene.get("text") or [scene.get("scene_text", "")]).strip()
        text = clean_voice_text(raw)
        if not text:
            continue
        duration_target = float(scene.get("duration", 5.0))
        safe_text = fit_text_to_duration(text, duration_target)
        audio_path = output_dir / f"scene_{idx}.wav"
        success = _synthesize(safe_text, audio_path, voice or "alloy")
        if not success:
            continue
        duration = _audio_duration(audio_path)
        if duration < duration_target:
            padded = output_dir / f"scene_{idx}_pad.wav"
            _pad_audio_to_duration(audio_path, padded, duration_target)
            audio_path = padded
            duration = duration_target
        voice_records.append({"scene": idx, "path": str(audio_path), "duration": duration or duration_target})

    concat_path = None
    if voice_records:
        concat_list = output_dir / "voice_concat.txt"
        concat_list.write_text(
            "\n".join(f"file '{Path(record['path']).resolve().as_posix()}'" for record in voice_records),
            encoding="utf-8",
        )
        concat_path = output_dir / "voiceover_full.m4a"
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(concat_list),
                "-c:a",
                "aac",
                str(concat_path),
            ],
            check=True,
            capture_output=True,
        )

    return voice_records, str(concat_path) if concat_path else None
