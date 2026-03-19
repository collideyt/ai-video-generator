import math
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
    total_duration = sum(float(scene["duration"]) for scene in timeline["timeline"])

    def _escape_drawtext(text: str) -> str:
        return (
            text.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace(",", "\\,")
            .replace("\n", " ")
        )

    def _escape_expr(expr: str) -> str:
        return expr.replace(",", "\\,")

    def _split_text_lines(text: str) -> list[str]:
        words = text.split()
        if len(words) <= 3:
            return [text]
        midpoint = max(2, math.ceil(len(words) / 2))
        first_line = " ".join(words[:midpoint]).strip()
        second_line = " ".join(words[midpoint:]).strip()
        return [line for line in [first_line, second_line] if line]

    def _caption_y(scene_type: str) -> str:
        if scene_type in {"hook", "problem"}:
            return "h*0.50"
        if scene_type == "proof":
            return "h*0.42"
        if scene_type == "cta":
            return "h*0.74"
        return "h*0.65"

    def _build_caption_filters(text_value: str | list[str], scene_type: str, duration: int | float) -> list[str]:
        phrases = text_value if isinstance(text_value, list) else [text_value]
        phrases = [phrase.strip().upper() for phrase in phrases if str(phrase).strip()]
        if not phrases:
            return []

        y_base = _caption_y(scene_type)
        line_offset = 82
        filters: list[str] = []
        phrase_duration = max(float(duration) / max(len(phrases), 1), 0.8)

        for phrase_index, phrase in enumerate(phrases):
            display_lines = _split_text_lines(phrase)
            start_t = round(phrase_index * phrase_duration, 2)
            end_t = round(min((phrase_index + 1) * phrase_duration, float(duration)), 2)
            enable_expr = _escape_expr(f"between(t,{start_t},{end_t})")

            for line_index, line in enumerate(display_lines):
                safe = _escape_drawtext(line)
                line_y_base = f"({y_base}+{line_index * line_offset})"
                filters.append(
                    "drawtext="
                    f"text='{safe}':"
                    "fontcolor=white:"
                    "fontsize=60:"
                    "x=(w-text_w)/2:"
                    f"y={line_y_base}:"
                    "alpha=1:"
                    "borderw=4:"
                    "bordercolor=black:"
                    "shadowx=2:"
                    "shadowy=2:"
                    "box=1:"
                    "boxcolor=black@0.4:"
                    "boxborderw=18:"
                    f"enable='{enable_expr}'"
                )

        return filters

    def _apply_transition_filters(filters: list[str], transition: str, duration: int | float) -> list[str]:
        transition_lower = transition.lower()
        if "fade" in transition_lower:
            fade_out_start = max(float(duration) - 0.35, 0)
            filters.append("fade=t=in:st=0:d=0.35")
            filters.append(f"fade=t=out:st={fade_out_start}:d=0.35")
        elif "slide" in transition_lower:
            slide_frames = max(int(float(duration) * 30), 1)
            filters.insert(
                2,
                f"crop=w=iw:h=ih:x='min((n/{slide_frames})*iw*0.08, iw*0.08)':y=0",
            )
        return filters

    def _build_asset_clip(
        asset: str | None,
        duration: float,
        output_path: Path,
        transition: str,
        scene_type: str,
        apply_caption: bool,
        caption_filters: list[str],
    ) -> None:
        base_filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=decrease",
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
        ]
        filters = base_filters[:]

        if asset and not asset.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
            if "zoom" in transition.lower() or scene_type == "hook":
                zoom_frames = max(int(float(duration) * 30), 1)
                filters.append(
                    f"zoompan=z='min(zoom+0.0015,1.4)':d={zoom_frames}:s={width}x{height}"
                )

        if apply_caption:
            filters.extend(caption_filters)

        filters = _apply_transition_filters(filters, transition, duration)

        if asset and asset.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
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
                str(output_path),
            ]
        elif asset:
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
                str(output_path),
            ]
        else:
            empty_filters = filters or [
                "drawtext=text=' ':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=h*0.65"
            ]
            cmd = [
                ffmpeg_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={width}x{height}:d={duration}",
                "-vf",
                ",".join(empty_filters),
                "-r",
                "30",
                str(output_path),
            ]

        subprocess.run(cmd, check=True, capture_output=True)

    def _scene_asset_durations(total_scene_duration: float, count: int) -> list[float]:
        if count <= 1:
            return [total_scene_duration]
        base = total_scene_duration / count
        durations = [round(base, 2) for _ in range(count)]
        durations[-1] = round(total_scene_duration - sum(durations[:-1]), 2)
        return durations

    scene_files = []
    for idx, scene in enumerate(timeline["timeline"], start=0):
        scene_path = output_dir / f"scene_{idx}.mp4"
        duration = float(scene["duration"])
        text_value = scene.get("text") or scene.get("scene_text") or ""
        scene_type = scene.get("type", "content")
        transition = scene.get("transition", "cut")
        scene_assets = [asset for asset in scene.get("assets", []) if asset] or [scene.get("asset")]
        scene_assets = [asset for asset in scene_assets if asset]

        caption_filters = _build_caption_filters(text_value, scene_type, duration)

        if len(scene_assets) <= 1:
            _build_asset_clip(
                scene_assets[0] if scene_assets else None,
                duration,
                scene_path,
                transition,
                scene_type,
                True,
                caption_filters,
            )
            scene_files.append(scene_path)
            continue

        subclip_paths: list[Path] = []
        subclip_durations = _scene_asset_durations(duration, len(scene_assets))
        for sub_idx, (asset, sub_duration) in enumerate(zip(scene_assets, subclip_durations)):
            subclip_path = output_dir / f"scene_{idx}_part_{sub_idx}.mp4"
            _build_asset_clip(
                asset,
                sub_duration,
                subclip_path,
                transition if sub_idx == len(scene_assets) - 1 else "cut",
                scene_type,
                True,
                caption_filters,
            )
            subclip_paths.append(subclip_path)

        scene_concat = output_dir / f"scene_{idx}_concat.txt"
        scene_concat.write_text(
            "\n".join(
                f"file '{str(path.resolve()).replace(chr(92), '/')}'" for path in subclip_paths
            ),
            encoding="utf-8",
        )
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(scene_concat),
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                str(scene_path),
            ],
            check=True,
            capture_output=True,
        )
        scene_files.append(scene_path)

    concat_list = output_dir / "concat.txt"
    concat_lines = []
    for clip in scene_files:
        clip_path = Path(clip)
        if not clip_path.exists():
            raise FileNotFoundError(f"Missing scene file: {clip_path}")
        abs_path = str(clip_path.resolve()).replace("\\", "/")
        concat_lines.append(f"file '{abs_path}'")
    concat_list.write_text("\n".join(concat_lines), encoding="utf-8")
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
            "[1:a]apad[a1];[2:a]volume=0.25,apad[a2];[a1][a2]amix=inputs=2:duration=longest[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-c:v",
            "copy",
            "-t",
            str(total_duration),
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
            "-af",
            "apad",
            "-t",
            str(total_duration),
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
            "-af",
            "apad",
            "-t",
            str(total_duration),
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
