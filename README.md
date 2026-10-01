# ComicCraft - AI Comic Story Creator

ComicCraft is a FastAPI web application that turns a story prompt, character, setting, tone, and art style into a five-panel comic and a PDF export.

## Architecture

- Frontend: HTML + CSS + Jinja2
- Backend: FastAPI
- Story outline: Gemini Flash
- Detailed narration/dialogue: Gemini Pro
- Images: Hugging Face Diffusers + Stable Diffusion (optional)
- PDF export: FPDF2

The original project documentation describes Gemini Flash, Gemini Pro, Stable Diffusion, FastAPI, Jinja2 and FPDF as the core stack.

## Important design choice

A single comic uses two Gemini text requests:
1. Generate the five-panel outline.
2. Generate narration/dialogue for the five panels.

Images are generated locally by Diffusers when `IMAGE_BACKEND=diffusers`.

For an easy first run, the default is `IMAGE_BACKEND=placeholder`. This lets you verify the complete website, Gemini flow and PDF export without downloading a large Stable Diffusion model.

## Windows setup

Open PowerShell in the ComicCraft folder:

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `.env` from `.env.example` and put your Gemini API key in it.

Start:

```powershell
uvicorn app.main:app --reload
```

Open:

http://127.0.0.1:8000

API docs:

http://127.0.0.1:8000/docs

## Real Stable Diffusion images

After the basic version works:

```powershell
pip install -r requirements-image.txt
```

Then change in `.env`:

```text
IMAGE_BACKEND=diffusers
```

The first image-generation run downloads the configured model and requires substantial disk space/RAM. A GPU is strongly recommended.

## Gemini quota note

If Gemini returns HTTP 429 / quota exceeded, the app displays a clear message instead of crashing. Wait for the retry period shown by Gemini and retry. Avoid repeatedly pressing Create My Comic because each attempt can consume API requests.

## API endpoints

- `GET /` — homepage
- `POST /generate` — browser form generation
- `POST /generate-comic/json` — JSON API
- `POST /test-image` — image test
- `GET /export-success` — export confirmation

## Project structure

```text
ComicCraft/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── routes.py
│   ├── schemas.py
│   └── services/
│       ├── gemini_flash.py
│       ├── gemini_pro.py
│       ├── image_generator.py
│       ├── layout_builder.py
│       └── exporters.py
├── templates/
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
├── static/
│   ├── css/style.css
│   ├── panels/
│   └── exports/
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-image.txt
└── README.md
```
