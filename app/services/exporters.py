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


def _clean_text(text: str) -> str:
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": "--",
        "\u2013": "-",
        "\u2026": "...",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "replace").decode("latin-1")


def save_pdf(layout: list[dict]) -> str:
    filename = f"comic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    output = EXPORTS_DIR / filename

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in layout:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        title = _clean_text(f"Panel {panel['panel_number']}: {panel['title']}")
        pdf.cell(0, 12, title, new_x="LMARGIN", new_y="NEXT")

        relative_image = panel["image_path"].removeprefix("/static/").replace("/", "/")
        image_path = STATIC_DIR / Path(relative_image)
        if image_path.exists():
            with Image.open(image_path) as img:
                width, height = img.size
            max_width = 180
            max_height = 100
            ratio = min(max_width / width, max_height / height)
            w_placed = width * ratio
            h_placed = height * ratio
            curr_y = pdf.get_y() + 2
            x_placed = (pdf.w - w_placed) / 2
            pdf.image(str(image_path), x=x_placed, y=curr_y, w=w_placed, h=h_placed)
            pdf.set_xy(pdf.l_margin, curr_y + h_placed + 8)

        if panel.get("scene_description"):
            pdf.set_font("Helvetica", "I", 11)
            pdf.multi_cell(0, 7, _clean_text(panel["scene_description"]), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

        if panel.get("caption"):
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, _clean_text(f"Caption: {panel['caption']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        pdf.set_font("Helvetica", "", 11)
        if panel.get("narration"):
            pdf.multi_cell(0, 7, _clean_text(f"Narration: {panel['narration']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)
        if panel.get("dialogue"):
            pdf.multi_cell(0, 7, _clean_text(f"Dialogue: {panel['dialogue']}"), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

    pdf.output(str(output))
    return f"/static/exports/{filename}"
