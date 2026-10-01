import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Current Gemini defaults. They can be changed in .env without editing code.
GEMINI_FLASH_MODEL = os.getenv("GEMINI_FLASH_MODEL", "gemini-3.8-flash").strip()
GEMINI_PRO_MODEL = os.getenv("GEMINI_PRO_MODEL", "gemini-3.1-pro-preview").strip()

# Local Diffusers image generation is optional because it is resource-heavy.
IMAGE_BACKEND = os.getenv("IMAGE_BACKEND", "placeholder").strip().lower()
SD_MODEL_ID = os.getenv(
    "SD_MODEL_ID",
    "stable-diffusion-v1-5/stable-diffusion-v1-5"
).strip()

HF_TOKEN = os.getenv("HF_TOKEN", "").strip()

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"

for directory in (PANELS_DIR, EXPORTS_DIR):
    directory.mkdir(parents=True, exist_ok=True)
