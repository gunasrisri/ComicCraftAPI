from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .routes import router

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate a five-panel AI comic from a story prompt.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app.state.templates = templates
app.include_router(router)
