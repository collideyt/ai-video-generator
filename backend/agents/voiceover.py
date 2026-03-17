import os
import subprocess
from pathlib import Path
import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"


def generate_voiceover(script: str, job_id: str) -> str | None:
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "voiceover.mp3"

    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            response = client.audio.speech.create(
                model="gpt-4o-mini-tts",
                voice="alloy",
                input=script,
            )
            response.stream_to_file(str(output_path))
            return str(output_path)
        except Exception:
            pass

    # Fallback: generate silent audio placeholder
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    if not ffmpeg_path:
        return None

    try:
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=44100:cl=stereo",
                "-t",
                "5",
                str(output_path),
            ],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        return None
    return str(output_path)
