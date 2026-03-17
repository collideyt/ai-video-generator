import math
import re


def split_script(script: str, target_duration: int = 30) -> list[dict]:
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", script) if s.strip()]
    if not sentences:
        sentences = [script.strip()]

    words = script.split()
    words_per_second = 2.2
    estimated_duration = max(5, math.ceil(len(words) / words_per_second))
    scale = target_duration / estimated_duration if estimated_duration else 1

    scenes = []
    for index, sentence in enumerate(sentences, start=1):
        duration = max(2, round(len(sentence.split()) / words_per_second))
        duration = max(2, round(duration * scale))
        scenes.append({"scene": index, "text": sentence, "duration": duration})

    return scenes
