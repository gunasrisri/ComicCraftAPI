import json
import time
import traceback
from pathlib import Path

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Form, HTTPException, Request
# pyrefly: ignore [missing-import]
from fastapi.responses import FileResponse, JSONResponse

from pydantic import ValidationError

from .config import EXPORTS_DIR
from .schemas import PromptRequest
from .services.gemini_flash import generate_outline
from .services.gemini_pro import generate_story
from .services.image_generator import generate_image
from .services.layout_builder import build_comic_layout
from .services.exporters import save_pdf

router = APIRouter()


def _error_message(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        error_msgs = []
        for err in exc.errors():
            field = " -> ".join(str(loc) for loc in err.get("loc", []))
            error_msgs.append(f"Field '{field}': {err.get('msg')}")
        return "Please check your inputs: " + "; ".join(error_msgs)
    message = str(exc)
    if "503" in message or "unavailable" in message.lower() or "demand" in message.lower():
        return (
            "Google's Gemini model is currently experiencing high demand (503). "
            "Please wait a moment and try clicking 'Create My Comic' again."
        )
    if "429" in message or "quota" in message.lower() or "rate" in message.lower():
        return (
            "Gemini API quota/rate limit reached. Wait for the retry period shown "
            "by Gemini and try again. This project uses two Gemini text requests "
            "per comic: one for the 5-panel outline and one for narration."
        )
    return message


def _generate_all(data: PromptRequest):
    outline = generate_outline(
        data.story_prompt,
        data.character_name,
        data.setting,
        data.tone,
        data.art_style,
    )
    stories = generate_story(outline, data.character_name, data.tone)

    image_paths = []
    for index, panel in enumerate(outline, start=1):
        image_paths.append(
            generate_image(
                panel["image_prompt"],
                index,
                panel.get("title", "comic"),
            )
        )

    layout = build_comic_layout(outline, stories, image_paths)
    pdf_path = save_pdf(layout)
    return layout, pdf_path


@router.get("/")
async def home(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "index.html",
        {"request": request},
    )


@router.post("/generate")
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):
    try:
        data = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        layout, pdf_path = _generate_all(data)
        return request.app.state.templates.TemplateResponse(
            request,
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "pdf_path": pdf_path,
            },
        )
    except Exception as exc:
        traceback.print_exc()
        status_code = 400 if isinstance(exc, ValidationError) else (429 if "429" in str(exc) else (503 if "503" in str(exc) else 500))
        return request.app.state.templates.TemplateResponse(
            request,
            "index.html",
            {
                "request": request,
                "error": _error_message(exc),
            },
            status_code=status_code,
        )


@router.post("/generate-comic/json")
async def generate_json(data: PromptRequest):
    try:
        layout, pdf_path = _generate_all(data)
        return JSONResponse({
            "success": True,
            "layout": layout,
            "pdf_path": pdf_path,
        })
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=_error_message(exc))


@router.get("/download/{filename}")
async def download(filename: str):
    safe_name = Path(filename).name
    path = EXPORTS_DIR / safe_name
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get("/export-success")
async def export_success(request: Request):
    return request.app.state.templates.TemplateResponse(
        request,
        "export_success.html",
        {"request": request},
    )


@router.post("/test-image")
async def test_image(prompt: str = Form(...)):
    try:
        image_path = generate_image(prompt, 0, "test_image")
        return {"success": True, "image_path": image_path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
