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

VIDEO_EXTENSIONS = (".mp4", ".mov", ".mkv", ".webm")


def _ken_burns(width: int, height: int, duration: float) -> str:
    zoom_width = max(int(width * 1.2), width + 2)
    zoom_height = max(int(height * 1.2), height + 2)
    frames = max(int(float(duration) * 30), 1)
    return (
        f"scale={zoom_width}:{zoom_height}:force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan=z='min(zoom+0.0015,1.2)':d={frames}:s={width}x{height}:fps=30"
    )


def _generate_placeholder(output: Path, width: int, height: int, duration: float, label: str, color: str = "gray") -> None:
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c={color}:s={width}x{height}:d={duration}",
            "-vf",
            f"drawtext=text='{label}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=h*0.45",
            "-r",
            "30",
            "-an",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output),
        ],
        check=True,
        capture_output=True,
    )


def _build_asset_clip(asset: str | None, duration: float, output_path: Path, caption_filters: list[str], width: int, height: int, transition_duration: float, ffmpeg_path: str) -> None:
    if asset and asset.lower().endswith(VIDEO_EXTENSIONS):
        filters = [
            f"scale={width}:{height}:force_original_aspect_ratio=increase",
            f"crop={width}:{height}",
            _ken_burns(width, height, duration),
            "setsar=1",
        ]
    elif asset:
        filters = [
            _ken_burns(width, height, duration),
            "setsar=1",
        ]
    else:
        _generate_placeholder(output_path, width, height, duration, "AI SCENE")
        return

    if caption_filters:
        filters.extend(caption_filters)
    fade_out_start = max(duration - transition_duration, 0.0)
    filters.append(f"fade=t=in:st=0:d={transition_duration}")
    filters.append(f"fade=t=out:st={fade_out_start}:d={transition_duration}")

    final_filter = ",".join(filters)
    cmd = [
        ffmpeg_path,
        "-y",
        "-loop" if asset and not asset.lower().endswith(VIDEO_EXTENSIONS) else "-stream_loop",
        "-1",
        "-i",
        asset if asset else f"color=c=black:s={width}x{height}",
        "-t",
        str(duration),
        "-vf",
        final_filter,
        "-r",
        "30",
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        str(output_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    if not output_path.exists():
        raise FileNotFoundError(f"Scene file missing: {output_path}")


def _attach_audio(video_path: Path, audio_path: str | None, duration: float, output_path: Path, transition_duration: float, ffmpeg_path: str) -> None:
    if audio_path:
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(video_path),
            "-i",
            audio_path,
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-af",
            f"afade=t=in:d={transition_duration},afade=t=out:st={max(duration-transition_duration,0)}:d={transition_duration}",
            "-shortest",
            "-t",
            str(duration),
            str(output_path),
        ]
    else:
        cmd = [
            ffmpeg_path,
            "-y",
            "-i",
            str(video_path),
            "-f",
            "lavfi",
            "-i",
            "anullsrc=channel_layout=stereo:sample_rate=44100",
            "-shortest",
            "-t",
            str(duration),
            "-map",
            "0:v",
            "-map",
            "1:a",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-af",
            f"afade=t=in:d={transition_duration},afade=t=out:st={max(duration-transition_duration,0)}:d={transition_duration}",
            str(output_path),
        ]
    subprocess.run(cmd, check=True, capture_output=True)
    if not output_path.exists():
        raise FileNotFoundError(f"Scene with audio missing: {output_path}")


def render_video(
    timeline: dict,
    assets: list[str],
    voiceover_records: list[dict] | None,
    captions: str | None,
    logo: str | None,
    music: str | None,
    job_id: str,
    specs: dict,
    output_filename: str | None = None,
) -> str:
    output_dir = OUTPUTS_DIR / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    print("Starting FFmpeg render")
    print("FFmpeg binary:", ffmpeg_path)
    print("Scene rendering started")

    aspect_ratio = str(specs.get("aspect_ratio") or "9:16")
    width, height = ASPECT_RATIOS.get(aspect_ratio, (1080, 1920))
    total_duration = sum(float(scene["duration"]) for scene in timeline.get("timeline", []))
    transition_duration = 0.5

    def _scene_asset_durations(total_scene_duration: float, count: int) -> list[float]:
        if count <= 1:
            return [total_scene_duration]
        base = total_scene_duration / count
        durations = [round(base, 2) for _ in range(count)]
        durations[-1] = round(total_scene_duration - sum(durations[:-1]), 2)
        return durations

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
        if len(words) <= 4:
            return [text]
        if len(words) <= 8:
            midpoint = max(2, math.ceil(len(words) / 2))
            first_line = " ".join(words[:midpoint]).strip()
            second_line = " ".join(words[midpoint:]).strip()
            return [line for line in [first_line, second_line] if line]

        chunk = math.ceil(len(words) / 3)
        lines = [
            " ".join(words[index : index + chunk]).strip()
            for index in range(0, len(words), chunk)
        ]
        return [line for line in lines if line]

    def _build_caption_filters(text_value: str | list[str], duration: float) -> list[str]:
        phrases = text_value if isinstance(text_value, list) else [text_value]
        phrases = [phrase.strip().upper() for phrase in phrases if str(phrase).strip()]
        if not phrases:
            return []

        filters: list[str] = []
        phrase_duration = max(float(duration) / max(len(phrases), 1), 0.65)

        for phrase_index, phrase in enumerate(phrases):
            display_lines = _split_text_lines(phrase)
            start_t = round(phrase_index * phrase_duration, 2)
            end_t = round(min((phrase_index + 1) * phrase_duration, float(duration)), 2)
            enable_expr = _escape_expr(f"between(t,{start_t},{end_t})")

            for line_index, line in enumerate(display_lines):
                safe = _escape_drawtext(line)
                y_position = f"h*0.75+{line_index * 84}"
                filters.append(
                    "drawtext="
                    f"text='{safe}':"
                    "x=(w-text_w)/2:"
                    f"y={y_position}:"
                    "fontsize=72:"
                    "fontcolor=white:"
                    "borderw=4:"
                    "bordercolor=black:"
                    f"enable='{enable_expr}'"
                )

        return filters

    scene_files: list[Path] = []
    for idx, scene in enumerate(timeline["timeline"], start=0):
        base_scene_path = output_dir / f"scene_{idx}.mp4"
        duration = float(scene["duration"])
        text_value = scene.get("text") or scene.get("scene_text") or ""
        scene_assets = [asset for asset in scene.get("assets", []) if asset] or [scene.get("asset")]
        scene_assets = [asset for asset in scene_assets if asset]
        caption_filters = _build_caption_filters(text_value, duration)

        try:
            if len(scene_assets) <= 1:
                asset_for_scene = scene_assets[0] if scene_assets else None
                _build_asset_clip(asset_for_scene, duration, base_scene_path, caption_filters, width, height, transition_duration, ffmpeg_path)
            else:
                subclip_paths: list[Path] = []
                sub_durations = _scene_asset_durations(duration, len(scene_assets))
                for sub_idx, (asset, sub_duration) in enumerate(zip(scene_assets, sub_durations)):
                    sub_path = output_dir / f"scene_{idx}_part_{sub_idx}.mp4"
                    _build_asset_clip(asset, sub_duration, sub_path, [], width, height, transition_duration, ffmpeg_path)
                    subclip_paths.append(sub_path)

                concat_file = output_dir / f"scene_{idx}_concat.txt"
                concat_entries = [f"file '{str(p.resolve()).replace('\\\\', '/')}'" for p in subclip_paths]
                concat_file.write_text("\n".join(concat_entries), encoding="utf-8")
                scene_base = output_dir / f"scene_{idx}_base.mp4"
                subprocess.run(
                    [
                        ffmpeg_path,
                        "-y",
                        "-f",
                        "concat",
                        "-safe",
                        "0",
                        "-i",
                        str(concat_file),
                        "-c:v",
                        "libx264",
                        "-pix_fmt",
                        "yuv420p",
                        str(scene_base),
                    ],
                    check=True,
                    capture_output=True,
                )

                if caption_filters:
                    subprocess.run(
                        [
                            ffmpeg_path,
                            "-y",
                            "-i",
                            str(scene_base),
                            "-vf",
                            ",".join(caption_filters),
                            "-r",
                            "30",
                            "-an",
                            "-c:v",
                            "libx264",
                            "-pix_fmt",
                            "yuv420p",
                            str(base_scene_path),
                        ],
                        check=True,
                        capture_output=True,
                    )
                else:
                    base_scene_path = scene_base
        except Exception:
            if scene_assets and Path(scene_assets[0]).exists():
                base_scene_path = Path(scene_assets[0])
            else:
                _generate_placeholder(base_scene_path, width, height, duration, f"SCENE {idx+1}")

        if not base_scene_path.exists():
            if scene_assets and Path(scene_assets[0]).exists():
                base_scene_path = Path(scene_assets[0])
            else:
                _generate_placeholder(base_scene_path, width, height, duration, f"SCENE {idx+1}")

        voice_path = scene.get("voice")
        with_audio = output_dir / f"scene_{idx}_a.mp4"
        _attach_audio(base_scene_path, voice_path, duration, with_audio, transition_duration, ffmpeg_path)
        scene_files.append(with_audio)

    merged_path = output_dir / "merged.mp4"
    concat_list = output_dir / "concat_scenes.txt"
    if not scene_files:
        dummy = output_dir / "dummy.mp4"
        _generate_placeholder(dummy, width, height, total_duration, "SCENE")
        scene_files = [dummy]

    concat_entries = [f"file '{str(p.resolve()).replace('\\\\', '/')}'" for p in scene_files]
    concat_list.write_text("\n".join(concat_entries), encoding="utf-8")
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
            "-c",
            "copy",
            str(merged_path),
        ],
        check=True,
        capture_output=True,
    )
    if not merged_path.exists():
        raise FileNotFoundError(f"Merged video missing at {merged_path}")

    bgm_path = music
    if not bgm_path:
        bgm_path = output_dir / "default_bgm.wav"
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"anoisesrc=color=pink:amplitude=0.3:duration={total_duration}",
                "-af",
                "volume=0.25",
                str(bgm_path),
            ],
            check=True,
            capture_output=True,
        )
        bgm_path = str(bgm_path)

    final_path = output_dir / (output_filename or "final_video.mp4")
    subprocess.run(
        [
            ffmpeg_path,
            "-y",
            "-i",
            str(merged_path),
            "-i",
            str(bgm_path),
            "-filter_complex",
            f"[0:a]volume=1.0[a0];[1:a]aloop=loop=-1:size=2e+09,atrim=0:{total_duration},volume=0.25[a1];[a0][a1]amix=inputs=2:duration=shortest[aout]",
            "-map",
            "0:v",
            "-map",
            "[aout]",
            "-t",
            str(total_duration),
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            str(final_path),
        ],
        check=True,
        capture_output=True,
    )

    if not final_path.exists():
        raise FileNotFoundError(f"Final video missing at {final_path}")

    return str(final_path)
