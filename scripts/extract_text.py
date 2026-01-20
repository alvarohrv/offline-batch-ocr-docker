import json
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image
import pdfplumber

# -----------------------------
# Configuración básica
# -----------------------------
DOCS_DIR = Path("/app/docs")
OUTPUT_DIR = Path("/app/output")
OUTPUT_FILE = OUTPUT_DIR / "raw_ocr.json"
LANG = "spa"  # español para tesseract

# -----------------------------
# Utilidades
# -----------------------------
def is_pdf(file_path: Path) -> bool:
    return file_path.suffix.lower() == ".pdf"


def is_image(file_path: Path) -> bool:
    return file_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]







def institute_from_path(file_path: Path, docs_dir: Path) -> str:
    """
    Obtiene el nombre del instituto a partir de la carpeta inmediata bajo docs.

    - Si el archivo está directamente en /app/docs => "undefined"
    - Si está en /app/docs/<carpeta>/archivo.pdf => nombre de carpeta en Pascal Case
      reemplazando '_' por ' '.
    """
    try:
        rel = file_path.relative_to(docs_dir)
    except ValueError:
        return "undefined"

    # rel.parts:
    # - ('archivo.pdf',) => fuera de carpeta
    # - ('SENA', 'archivo.pdf') => dentro de carpeta
    # - ('SENA', 'sub', 'archivo.pdf') => mantiene institute='Sena' (carpeta inmediata)
    if len(rel.parts) <= 1:
        return "undefined"

    folder = rel.parts[0]
    words = folder.replace("_", " ").split()
    return " ".join(w.capitalize() for w in words) if words else "undefined"


# -----------------------------
# Verificar si un PDF tiene texto
# -----------------------------
def pdf_has_text(pdf_path: Path) -> bool:
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    return True
    except Exception:
        pass
    return False


# -----------------------------
# OCR para PDF
# -----------------------------
def ocr_pdf(pdf_path: Path) -> dict:
    # CASO 1: PDF ya tiene texto (digital / firmado)
    if pdf_has_text(pdf_path):
        text_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text_pages.append(
                    {
                        "page": i + 1,
                        "text": page.extract_text() or "",
                    }
                )

        return {
            "file": pdf_path.name,
            "type": "pdf_digital",
            "pages": len(text_pages),
            "raw_text": text_pages,
            "note": "Texto extraído sin OCR (PDF digital)",
        }

    # CASO 2: PDF escaneado → OCR
    ocr_pdf_path = pdf_path.with_name(f"{pdf_path.stem}_ocr.pdf")

    subprocess.run(
        [
            "ocrmypdf",
            "--language",
            LANG,
            "--force-ocr",
            str(pdf_path),
            str(ocr_pdf_path),
        ],
        check=True,
    )

    text_pages = []
    with pdfplumber.open(ocr_pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text_pages.append(
                {
                    "page": i + 1,
                    "text": page.extract_text() or "",
                }
            )

    return {
        "file": pdf_path.name,
        "type": "pdf_scanned",
        "pages": len(text_pages),
        "raw_text": text_pages,
        "note": "Texto extraído con OCRmyPDF",
    }


# -----------------------------
# OCR para imágenes
# -----------------------------
def ocr_image(image_path: Path) -> dict:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang=LANG)
    return {
        "file": image_path.name,
        "type": "image",
        "pages": 1,
        "raw_text": text,
    }


# -----------------------------
# Main
# -----------------------------
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []

    if not DOCS_DIR.exists():
        print(f"⚠️ No existe el directorio: {DOCS_DIR}")
        return

    # Recorre recursivamente /docs incluyendo subcarpetas
    all_paths = sorted([p for p in DOCS_DIR.rglob("*") if p.is_file()])

    if not all_paths:
        print("⚠️ No hay archivos en /docs")
        return

    for file_path in all_paths:
        institute = institute_from_path(file_path, DOCS_DIR)
        rel_path = str(file_path.relative_to(DOCS_DIR))

        try:
            print(f"📄 Procesando: {rel_path}")

            if is_pdf(file_path):
                result = ocr_pdf(file_path)
            elif is_image(file_path):
                result = ocr_image(file_path)
            else:
                print(f"⏭️ Formato no soportado: {file_path.name}")
                continue

            # Agrega metadata solicitada
            result["institute"] = institute
            result["path"] = rel_path

            results.append(result)

        except Exception as e:
            print(f"❌ Error procesando {file_path.name}: {e}")
            results.append(
                {
                    "file": file_path.name,
                    "path": rel_path,
                    "institute": institute,
                    "error": str(e),
                }
            )

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR finalizado. Resultado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
