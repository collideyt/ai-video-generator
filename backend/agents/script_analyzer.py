import math
import re

SCENE_SPLIT_RE = re.compile(r"\n?\s*-{3,}\s*\n?")
SCENE_HEADER_RE = re.compile(
    r"^\[\s*(?P<scene_type>[^|\]]+?)\s*\|\s*(?P<time_range>[^|\]]+?)(?:\s*\|\s*(?P<style>[^\]]+?))?\s*\]\s*$",
    re.MULTILINE,
)
TIME_RANGE_RE = re.compile(
    r"^\s*(?P<start>\d+(?:\.\d+)?)s?\s*-\s*(?P<end>\d+(?:\.\d+)?)s?\s*$",
    re.IGNORECASE,
)
FIELD_RE = re.compile(r"^(TEXT|VISUAL|TRANSITION)\s*:\s*(.*)$", re.IGNORECASE)


def _normalize_scene_type(scene_type: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", scene_type.strip().lower()).strip("_") or "content"


def _split_plain_text_script(script: str, target_duration: int = 30) -> list[dict]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not sentences:
        sentences = [script.strip()]

    words = script.split()
    words_per_second = 2.2
    estimated_duration = max(5, math.ceil(len(words) / words_per_second))
    scale = target_duration / estimated_duration if estimated_duration else 1

    scenes = []
    current_start = 0
    for index, sentence in enumerate(sentences, start=1):
        duration = max(2, round(len(sentence.split()) / words_per_second))
        duration = max(2, round(duration * scale))
        scene_type = "hook" if index == 1 else "cta" if index == len(sentences) else "content"
        scenes.append(
            {
                "scene": index,
                "scene_type": scene_type,
                "text": [sentence],
                "duration": duration,
                "visual_hint": "",
                "transition": "cut",
                "style": "default",
                "start": current_start,
                "end": current_start + duration,
                "raw_text": sentence,
            }
        )
        current_start += duration

    return scenes


def _parse_time_range(raw_range: str) -> tuple[float, float, int]:
    match = TIME_RANGE_RE.match(raw_range.strip())
    if not match:
        raise ValueError(f"Invalid scene time range: {raw_range}")

    start = float(match.group("start"))
    end = float(match.group("end"))
    if end <= start:
        raise ValueError(f"Scene end time must be greater than start time: {raw_range}")

    duration = end - start
    if duration.is_integer():
        duration_value = int(duration)
    else:
        duration_value = duration

    return start, end, duration_value


def parse_structured_script(script: str, target_duration: int = 30) -> list[dict]:
    blocks = [block.strip() for block in SCENE_SPLIT_RE.split(script.strip()) if block.strip()]
    if not blocks or not any(SCENE_HEADER_RE.search(block) for block in blocks):
        return _split_plain_text_script(script, target_duration=target_duration)

    scenes: list[dict] = []

    for index, block in enumerate(blocks, start=1):
        header_match = SCENE_HEADER_RE.search(block)
        if not header_match:
            continue

        fields = {"TEXT": [], "VISUAL": "", "TRANSITION": "cut"}
        current_field = None
        body = block[header_match.end():].strip()

        for raw_line in body.splitlines():
            line = raw_line.strip()
            if not line:
                continue

            field_match = FIELD_RE.match(line)
            if field_match:
                current_field = field_match.group(1).upper()
                value = field_match.group(2).strip()
            elif current_field:
                value = line
            else:
                continue

            if current_field == "TEXT" and value:
                fields["TEXT"].append(value)
            elif current_field == "VISUAL" and value:
                fields["VISUAL"] = f"{fields['VISUAL']} {value}".strip()
            elif current_field == "TRANSITION" and value:
                fields["TRANSITION"] = value.lower()

        start, end, duration = _parse_time_range(header_match.group("time_range"))
        text_lines = fields["TEXT"] or [""]
        combined_text = " ".join(text_lines).strip()

        scenes.append(
            {
                "scene": index,
                "scene_type": _normalize_scene_type(header_match.group("scene_type")),
                "start": start,
                "end": end,
                "duration": duration,
                "text": text_lines,
                "visual_hint": fields["VISUAL"],
                "transition": fields["TRANSITION"],
                "style": (header_match.group("style") or "default").strip().lower(),
                "raw_text": combined_text,
            }
        )

    print(f"Structured scenes detected: {len(scenes)}")
    return scenes


def split_script(script: str, target_duration: int = 30) -> list[dict]:
    scenes = parse_structured_script(script, target_duration=target_duration)
    print(f"Total scenes parsed: {len(scenes)}")
    return scenes
