import json
import re

from google import genai

from ..config import GEMINI_API_KEY, GEMINI_PRO_MODEL


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
        raise ValueError("Gemini did not return a JSON story list.")
    return json.loads(text[start:end + 1])


def generate_story(outline: list[dict], character_name: str, tone: str) -> list[dict]:
    compact_outline = json.dumps(outline, ensure_ascii=False)

    prompt = f"""
Expand this five-panel comic outline into narration and dialogue.

Main character: {character_name}
Tone: {tone}

Outline:
{compact_outline}

Return ONLY valid JSON as an array of exactly 5 objects.
Each object must contain:
panel_number, caption, narration, dialogue

Keep dialogue short enough to fit inside a comic panel.
Do not add markdown or extra commentary.
"""

    response = _client().models.generate_content(
        model=GEMINI_PRO_MODEL,
        contents=prompt,
    )
    stories = _extract_json(response.text)

    if not isinstance(stories, list) or len(stories) != 5:
        raise ValueError("Expected exactly 5 story panels from Gemini.")

    for i, story in enumerate(stories, start=1):
        story["panel_number"] = i
        story.setdefault("caption", "")
        story.setdefault("narration", "")
        story.setdefault("dialogue", "")

    return stories
