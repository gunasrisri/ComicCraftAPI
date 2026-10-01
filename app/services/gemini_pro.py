import json
import re

from google import genai

from ..config import GEMINI_API_KEY, GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL


_genai_client = None

def _client():
    global _genai_client
    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to the .env file."
        )
    if _genai_client is None:
        _genai_client = genai.Client(api_key=GEMINI_API_KEY)
    return _genai_client


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

    models_to_try = [GEMINI_PRO_MODEL]
    for alt in ["gemini-flash-latest", "gemini-3.6-flash", "gemini-flash-lite-latest"]:
        if alt not in models_to_try:
            models_to_try.append(alt)

    response = None
    last_exc = None
    for model_name in models_to_try:
        try:
            response = _client().models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                break
        except Exception as exc:
            last_exc = exc
            continue
    else:
        raise last_exc
    stories = _extract_json(response.text)

    if not isinstance(stories, list) or len(stories) != 5:
        raise ValueError("Expected exactly 5 story panels from Gemini.")

    for i, story in enumerate(stories, start=1):
        story["panel_number"] = i
        story.setdefault("caption", "")
        story.setdefault("narration", "")
        story.setdefault("dialogue", "")

    return stories
