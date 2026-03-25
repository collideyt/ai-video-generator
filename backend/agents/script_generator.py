import json
import random
from datetime import datetime

STYLE_TONES = {
    "cinematic": {
        "hook": "A dramatic opening shot that instantly pulls the viewer in.",
        "content": "Vivid, sensory descriptions that feel like a movie playing out.",
        "cta": "A confident, polished closing beat that leaves a clear next step.",
    },
    "doc": {
        "hook": "A curious, observational opener that hints at a bigger story.",
        "content": "Grounded, factual narration with human detail.",
        "cta": "A concise takeaway that invites action or reflection.",
    },
}


def _pick_style(style: str) -> dict:
    key = (style or "cinematic").lower()
    return STYLE_TONES.get(key, STYLE_TONES["cinematic"])


def _scene_text(prompt: str, tone: str, role: str) -> str:
    seed = random.randint(1000, 9999)
    base = prompt.strip().rstrip(".?!")
    if role == "hook":
        return f"{tone} Imagine {base} arriving in the next 30 seconds - hear the doors open and feel the first breath of air."
    if role == "content":
        return f"{tone} We follow the moment as {base} unfolds: textures, colors, voices, and a subtle shift that changes what you expect."
    return f"{tone} If this spoke to you, lean in - ask for a closer look today. Ref: {seed}."


def generate_script_from_prompt(prompt: str, style: str = "cinematic", duration: int = 30) -> str:
    """Generate a structured JSON script with distinct scenes."""
    print(f"Generating structured script from prompt: {prompt}")
    tone = _pick_style(style)
    base_duration = max(10, duration)
    hook_dur = 5
    cta_dur = 5
    content_dur = max(base_duration - hook_dur - cta_dur, 8)

    scenes = [
        {
            "type": "hook",
            "text": _scene_text(prompt, tone["hook"], "hook"),
            "duration": hook_dur,
        },
        {
            "type": "content",
            "text": _scene_text(prompt, tone["content"], "content"),
            "duration": content_dur,
        },
        {
            "type": "cta",
            "text": _scene_text(prompt, tone["cta"], "cta"),
            "duration": cta_dur,
        },
    ]

    payload = {"generated_at": datetime.utcnow().isoformat() + "Z", "style": style, "scenes": scenes}
    return json.dumps(payload, ensure_ascii=False, indent=2)
