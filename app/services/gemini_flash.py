import json
import re

from google import genai

from ..config import GEMINI_API_KEY, GEMINI_FLASH_MODEL


def _client():
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the .env file."
        )
    return genai.Client(api_key=GEMINI_API_KEY)


def _extract_json(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("Gemini did not return a JSON panel list.")
    return json.loads(text[start:end + 1])


def generate_outline(story_prompt: str, character_name: str, setting: str,
                     tone: str, art_style: str) -> list[dict]:
    prompt = f"""
Create exactly 5 panels for a personalized comic.

Story prompt: {story_prompt}
Main character: {character_name}
Setting: {setting}
Tone: {tone}
Art style: {art_style}

Return ONLY valid JSON as an array of exactly 5 objects.
Each object must contain:
panel_number, title, scene_description, image_prompt

Keep the story coherent from panel 1 to panel 5.
The image_prompt must be a detailed visual prompt suitable for a comic illustration.
Do not include markdown fences.
"""

    response = _client().models.generate_content(
        model=GEMINI_FLASH_MODEL,
        contents=prompt,
    )
    panels = _extract_json(response.text)

    if not isinstance(panels, list) or len(panels) != 5:
        raise ValueError("Expected exactly 5 comic panels from Gemini.")

    for i, panel in enumerate(panels, start=1):
        panel["panel_number"] = i
        panel.setdefault("title", f"Panel {i}")
        panel.setdefault("scene_description", "")
        panel.setdefault("image_prompt", "")

    return panels
