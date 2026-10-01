from datetime import datetime
from pathlib import Path
from fpdf import FPDF
from PIL import Image

from ..config import EXPORTS_DIR, STATIC_DIR


def _to_local_path(url_path: str) -> Path:
    # URL path looks like /static/panels/file.png
    relative = url_path.removeprefix("/static/").replace("/", str(Path("/").anchor))
    # Simpler and safer for this project:
    return STATIC_DIR / url_path.split("/static/", 1)[-1].replace("/", str(Path("/")))


def save_pdf(layout: list[dict]) -> str:
    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output = EXPORTS_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, f"Panel {panel['panel_number']}: {panel['title']}", ln=True)

        relative_image = panel["image_path"].removeprefix("/static/").replace("/", "/")
        image_path = STATIC_DIR / Path(relative_image)
        if image_path.exists():
            with Image.open(image_path) as img:
                width, height = img.size
            max_width = 180
            max_height = 100
            ratio = min(max_width / width, max_height / height)
            pdf.image(str(image_path), x=15, y=32, w=width * ratio, h=height * ratio)
            pdf.ln(max_height + 5)

        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, panel["scene_description"])

        pdf.set_font("Helvetica", "B", 11)
        if panel["caption"]:
            pdf.multi_cell(0, 7, f"Caption: {panel['caption']}")

        pdf.set_font("Helvetica", "", 11)
        if panel["narration"]:
            pdf.multi_cell(0, 7, f"Narration: {panel['narration']}")
        if panel["dialogue"]:
            pdf.multi_cell(0, 7, f"Dialogue: {panel['dialogue']}")

    pdf.output(str(output))
    return f"/static/exports/{filename}"
