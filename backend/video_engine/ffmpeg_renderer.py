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

    def _build_caption_filters(
        text_value: str | list[str],
        scene_type: str,
        duration: int | float,
        text_animation: str,
        text_layout: str,
    ) -> list[str]:
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

    def _apply_transition_filters(filters: list[str], transition: str, duration: int | float) -> list[str]:
        transition_lower = transition.lower()
        transition_in = min(0.22, max(float(duration) * 0.18, 0.08))
        transition_out = min(0.18, max(float(duration) * 0.14, 0.06))
        fade_out_start = max(float(duration) - transition_out, 0)

        if "fade" in transition_lower:
            filters.append(f"fade=t=in:st=0:d={transition_in}")
            filters.append(f"fade=t=out:st={fade_out_start}:d={transition_out}")
        elif "slide" in transition_lower:
            slide_x = _escape_expr(f"0.02*iw + (t/{max(duration, 0.1)})*(0.02*iw)")
            slide_y = _escape_expr(f"0.02*ih - (t/{max(duration, 0.1)})*(0.01*ih)")
            filters.append(
                f"crop=w=iw*0.96:h=ih*0.96:x='{slide_x}':y='{slide_y}'"
            )
        elif "zoom" in transition_lower:
            filters.append(f"fade=t=in:st=0:d={transition_in}")
        return filters

    def _motion_filter(duration: float, width_value: int, height_value: int) -> str:
        zoom_width = max(int(width_value * 1.2), width_value + 2)
        zoom_height = max(int(height_value * 1.2), height_value + 2)
        frames = max(int(float(duration) * 30), 1)
        return (
            f"scale={zoom_width}:{zoom_height}:force_original_aspect_ratio=increase,"
            f"crop={width_value}:{height_value},"
            f"zoompan=z='min(zoom+0.0015,1.2)':d={frames}:s={width_value}x{height_value}:fps=30"
        )

    def _overlay_captions(
        input_path: Path,
        output_path: Path,
        duration: float,
        caption_filters: list[str],
    ) -> None:
        if not caption_filters:
            input_path.replace(output_path)
            return

        final_filter = ",".join(caption_filters)
        print("FFmpeg caption filter:", final_filter)
        subprocess.run(
            [
                ffmpeg_path,
                "-y",
                "-i",
                str(input_path),
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
            ],
            check=True,
            capture_output=True,
        )

    def _subclip_transition(
        base_transition: str,
        scene_type: str,
        scene_preset: str,
        clip_index: int,
        clip_count: int,
    ) -> str:
        if clip_index == 0:
            return "cut"
        if scene_preset == "hook":
            sequence = ["cut", "zoom", "cut", "slide"]
        elif scene_preset == "problem":
            sequence = ["cut", "fade", "cut"]
        elif scene_preset == "shift":
            sequence = ["zoom", "cut", "zoom"]
        elif scene_preset == "proof":
            sequence = ["fade", "slide", "fade"]
        elif scene_preset == "cta":
            sequence = ["zoom", "cut", "fade"]
        elif scene_type in {"hook", "problem", "shift"}:
            sequence = ["cut", "slide", "zoom", "cut"]
        elif scene_type in {"proof", "future", "cta"}:
            sequence = ["slide", "zoom", "fade", "cut"]
        else:
            sequence = ["cut", "slide", "fade"]
        if clip_index == clip_count - 1 and base_transition:
            return base_transition
        return sequence[(clip_index - 1) % len(sequence)]

    def _build_asset_clip(
        asset: str | None,
        duration: float,
        output_path: Path,
        transition: str,
        scene_type: str,
        motion_style: str,
        motion_intensity: str,
        apply_caption: bool,
        caption_filters: list[str],
    ) -> None:
        if asset and asset.lower().endswith(VIDEO_EXTENSIONS):
            filters = [
                f"scale={width}:{height}:force_original_aspect_ratio=increase",
                f"crop={width}:{height}",
                f"zoompan=z='min(zoom+0.0015,1.2)':d={max(int(float(duration) * 30), 1)}:s={width}x{height}:fps=30",
                "setsar=1",
            ]
        else:
            filters = [
                _motion_filter(duration, width, height),
                "setsar=1",
            ]

        if apply_caption:
            filters.extend(caption_filters)

        filters = _apply_transition_filters(filters, transition, duration)
        final_filter = ",".join(filters)
        print("FFmpeg scene filter:", final_filter)

        if asset and asset.lower().endswith(VIDEO_EXTENSIONS):
            cmd = [
                ffmpeg_path,
                "-y",
                "-i",
                asset,
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
        else:
            empty_filters = filters or [
                "drawtext=text=' ':fontcolor=white:fontsize=70:x=(w-text_w)/2:y=h*0.40"
            ]
            cmd = [
                ffmpeg_path,
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={width}x{height}:d={duration}",
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

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode(errors="replace") if exc.stderr else ""
            print("FFmpeg scene render failed:", stderr)
            raise

    def _subclip_motion_style(
        clip_index: int,
        default_motion_style: str,
        motion_cycle: list[str],
    ) -> str:
        if motion_cycle:
            return motion_cycle[clip_index % len(motion_cycle)]
        return default_motion_style or "drift"

    def _scene_asset_durations(
        total_scene_duration: float,
        count: int,
        pace: str,
        clip_duration_range: list[float] | tuple[float, float] | None,
    ) -> list[float]:
        if count <= 1:
            return [total_scene_duration]

        if clip_duration_range and len(clip_duration_range) >= 2:
            min_duration = float(clip_duration_range[0])
            max_duration = float(clip_duration_range[1])
        elif pace == "fast":
            min_duration, max_duration = 0.5, 1.0
        elif pace == "slow":
            min_duration, max_duration = 1.0, 1.5
        else:
            min_duration, max_duration = 0.8, 1.3

        midpoint = round((min_duration + max_duration) / 2, 2)
        if pace == "fast":
            base_pattern = [min_duration, midpoint, max_duration, midpoint]
        elif pace == "slow":
            base_pattern = [midpoint, max_duration, midpoint, min_duration]
        else:
            base_pattern = [midpoint, min_duration, max_duration, midpoint]

        durations: list[float] = []
        remaining = round(total_scene_duration, 2)

        for idx in range(count):
            clips_left = count - idx
            if clips_left == 1:
                durations.append(round(max(remaining, min_duration), 2))
                break

            candidate = base_pattern[idx % len(base_pattern)]
            max_allowed = remaining - (clips_left - 1) * min_duration
            clip_duration = round(min(max(candidate, min_duration), min(max_duration, max_allowed)), 2)
            durations.append(clip_duration)
            remaining = round(remaining - clip_duration, 2)

        if durations:
            durations[-1] = round(total_scene_duration - sum(durations[:-1]), 2)
        return durations

    scene_files = []
    for idx, scene in enumerate(timeline["timeline"], start=0):
        scene_path = output_dir / f"scene_{idx}.mp4"
        duration = float(scene["duration"])
        text_value = scene.get("text") or scene.get("scene_text") or ""
        scene_type = scene.get("type", "content")
        scene_preset = scene.get("scene_preset", scene_type)
        transition = scene.get("transition", "cut")
        motion_style = scene.get("motion_style", "push_in")
        motion_intensity = scene.get("motion_intensity", "medium")
        motion_cycle = scene.get("subclip_motion_cycle", [motion_style])
        pace = scene.get("pace", "medium")
        text_animation = scene.get("text_animation", "fade_in")
        text_layout = scene.get("text_layout", "center_stack")
        clip_duration_range = scene.get("clip_duration_range", [0.8, 1.3])
        scene_assets = [asset for asset in scene.get("assets", []) if asset] or [scene.get("asset")]
        scene_assets = [asset for asset in scene_assets if asset]
        scene_assets.sort(key=lambda asset: 0 if asset.lower().endswith(VIDEO_EXTENSIONS) else 1)

        caption_filters = _build_caption_filters(text_value, scene_type, duration, text_animation, text_layout)

        if len(scene_assets) <= 1:
            _build_asset_clip(
                scene_assets[0] if scene_assets else None,
                duration,
                scene_path,
                transition,
                scene_type,
                motion_style,
                motion_intensity,
                True,
                caption_filters,
            )
            scene_files.append(scene_path)
            continue

        subclip_paths: list[Path] = []
        subclip_durations = _scene_asset_durations(duration, len(scene_assets), pace, clip_duration_range)
        for sub_idx, (asset, sub_duration) in enumerate(zip(scene_assets, subclip_durations)):
            subclip_path = output_dir / f"scene_{idx}_part_{sub_idx}.mp4"
            _build_asset_clip(
                asset,
                sub_duration,
                subclip_path,
                _subclip_transition(transition, scene_type, scene_preset, sub_idx, len(scene_assets)),
                scene_type,
                _subclip_motion_style(sub_idx, motion_style, motion_cycle),
                motion_intensity,
                False,
                [],
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
                str(scene_path.with_name(f"{scene_path.stem}_base.mp4")),
            ],
            check=True,
            capture_output=True,
        )
        _overlay_captions(
            scene_path.with_name(f"{scene_path.stem}_base.mp4"),
            scene_path,
            duration,
            caption_filters,
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
