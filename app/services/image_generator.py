from pathlib import Path
import re
import html

from PIL import Image, ImageDraw, ImageFont

from ..config import IMAGE_BACKEND, PANELS_DIR, SD_MODEL_ID, HF_TOKEN


_pipe = None


def _safe_name(text: str, index: int) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "_", text).strip("_")
    return f"panel_{index}_{slug[:40] or 'comic'}.png"


def _placeholder(prompt: str, index: int, filename: str) -> str:
    # Lightweight fallback so the complete app can run without a GPU/model download.
    image = Image.new("RGB", (1024, 1024), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((20, 20, 1004, 1004), outline="black", width=8)
    draw.text((55, 55), f"COMICCRAFT — PANEL {index}", fill="black")
    wrapped = prompt[:500]
    draw.text((55, 130), wrapped, fill="black")
    path = PANELS_DIR / filename
    image.save(path)
    return f"/static/panels/{filename}"


def _get_pipe():
    global _pipe
    if _pipe is not None:
        return _pipe

    import torch
    from diffusers import StableDiffusionPipeline

    kwargs = {}
    if HF_TOKEN:
        kwargs["token"] = HF_TOKEN

    _pipe = StableDiffusionPipeline.from_pretrained(
        SD_MODEL_ID,
        **kwargs,
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    _pipe = _pipe.to(device)
    return _pipe


def generate_image(image_prompt: str, index: int, title: str = "comic") -> str:
    filename = _safe_name(title, index)

    if IMAGE_BACKEND != "diffusers":
        return _placeholder(image_prompt, index, filename)

    try:
        pipe = _get_pipe()
        prompt = (
            f"{image_prompt}, comic book illustration, clear composition, "
            "consistent character appearance, expressive faces, cinematic lighting"
        )
        result = pipe(prompt, num_inference_steps=25, guidance_scale=7.0)
        result.images[0].save(PANELS_DIR / filename)
        return f"/static/panels/{filename}"
    except Exception:
        # Keep the web app usable if the local model cannot load on the machine.
        return _placeholder(image_prompt, index, filename)
