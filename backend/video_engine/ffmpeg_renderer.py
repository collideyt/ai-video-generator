import subprocess
from pathlib import Path
import imageio_ffmpeg

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"

ASPECT_RATIOS = {
    "16:9": (1920, 1080),
    "9:16": (1080, 1920),
    "1:1": (1080, 1080),
}


def render_video(
    timeline: dict,
    assets: list[str],
    voiceover: str | None,
    captions: str | None,
    logo: str | None,
    music: str | None,
    job_id: str,
    specs: dict,
) -> str:
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print("Starting FFmpeg render")
    print("FFmpeg binary:", ffmpeg_path)
    print("Scene rendering started")

    width, height = ASPECT_RATIOS.get(specs.get("aspect_ratio"), (1080, 1920))

    def _escape_drawtext(text: str) -> str:
        # Escape characters used by ffmpeg drawtext
        return (
            text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("\n", " ")
        )

    def _build_text_overlay(text: str) -> str:
        safe = _escape_drawtext(text) if text else " "
        print("Adding text overlay")
        return (
            f"drawtext=text='{safe}':fontcolor=white:fontsize=60:"
            f"x=(w-text_w)/2:y=h-200:box=1:boxcolor=black@0.4:boxborderw=10"
        )

    scene_files = []
    for idx, scene in enumerate(timeline["timeline"], start=0):
        scene_path = output_dir / f"scene_{idx}.mp4"
        asset = scene.get("asset")
        duration = scene["duration"]
        scene_text = scene.get("text") or scene.get("scene_text") or ""
        transition = scene.get("transition", "cut")

        if asset and asset.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
            filters = [
                f"scale={width}:{height}:force_original_aspect_ratio=decrease",
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                _build_text_overlay(scene_text),
            ]
            if transition == "fade":
                fade_out_start = max(duration - 0.5, 0)
                filters.append(f"fade=t=in:st=0:d=0.5")
                filters.append(f"fade=t=out:st={fade_out_start}:d=0.5")
            cmd = [
                ffmpeg_path,
                "-y",
                "-i",
                asset,
                "-t",
                str(duration),
                "-vf",
                ",".join(filters),
                "-r",
                "30",
                str(scene_path),
            ]
        elif asset:
            filters = [
                f"scale={width}:{height}:force_original_aspect_ratio=decrease",
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
                _build_text_overlay(scene_text),
            ]
            if transition == "zoom":
                print("Applying zoom effect")
                zoom_frames = max(int(duration * 30), 1)
                filters.insert(
                    2,
                    f"zoompan=z='min(zoom+0.0015,1.4)':d={zoom_frames}:s={width}x{height}",
                )
            elif transition == "fade":
                fade_out_start = max(duration - 0.5, 0)
                filters.append(f"fade=t=in:st=0:d=0.5")
                filters.append(f"fade=t=out:st={fade_out_start}:d=0.5")
            cmd = [
                ffmpeg_path,
                "-y",
                "-loop",
                "1",
                "-i",
                asset,
                "-t",
                str(duration),
                "-vf",
                ",".join(filters),
                "-r",
                "30",
                str(scene_path),
            ]
        else:
            text_filter = _build_text_overlay(scene_text)
            cmd = [
                ffmpeg_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={width}x{height}:d={duration}",
                "-vf",
                text_filter,
                "-r",
                "30",
                str(scene_path),
            ]

        subprocess.run(cmd, check=True, capture_output=True)
        scene_files.append(scene_path)
    concat_list = output_dir / "concat.txt"
    concat_lines = []
    for clip in scene_files:
        clip_path = Path(clip)
        if not clip_path.exists():
            raise FileNotFoundError(f"Missing scene file: {clip_path}")
        abs_path = str(clip_path.resolve()).replace("\\", "/")
        concat_lines.append(f"file '{abs_path}'")
    concat_list.write_text("\n".join(concat_lines))
    print("Concat file:", str(concat_list))

    temp_video = output_dir / "temp_video.mp4"
    try:
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
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(temp_video),
            ],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if exc.stderr else ""
        print("FFmpeg concat failed:", stderr)
        raise

    final_path = output_dir / "final_video.mp4"
    print("Mixing audio tracks")
    if voiceover and music:
        audio_cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(temp_video),
            "-i",
            voiceover,
            "-i",
            music,
            "-filter_complex",
            "[2:a]volume=0.25[a2];[1:a][a2]amix=inputs=2[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-shortest",
            str(final_path),
        ]
    elif voiceover:
        audio_cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(temp_video),
            "-i",
            voiceover,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-shortest",
            str(final_path),
        ]
    elif music:
        audio_cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(temp_video),
            "-i",
            music,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-shortest",
            str(final_path),
        ]
    else:
        audio_cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(temp_video),
            "-c:v",
            "copy",
            str(final_path),
        ]

    try:
        subprocess.run(audio_cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.decode(errors="replace") if exc.stderr else ""
        print("FFmpeg audio mix failed:", stderr)
        raise

    return str(final_path)
