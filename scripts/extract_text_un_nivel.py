import os
import json
import subprocess
from pathlib import Path

import pytesseract
from PIL import Image
import pdfplumber

# Logica:
# PDF escaneado (sin texto)	OCRmyPDF
# PDF digital (texto seleccionable / firmado)	Extraer texto directo


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


# -----------------------------
# OCR para PDF
# -----------------------------

def ocr_pdf(pdf_path: Path) -> dict:
    # CASO 1: PDF ya tiene texto (digital / firmado)
    if pdf_has_text(pdf_path):
        text_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text_pages.append({
                    "page": i + 1,
                    "text": page.extract_text() or ""
                })

        return {
            "file": pdf_path.name,
            "type": "pdf_digital",
            "pages": len(text_pages),
            "raw_text": text_pages,
            "note": "Texto extraído sin OCR (PDF digital)"
        }
    # CASO 2: PDF escaneado → OCR


    """
    Aplica OCRmyPDF y luego extrae texto con pdfplumber
    """
    ocr_pdf_path = pdf_path.with_name(f"{pdf_path.stem}_ocr.pdf")

    # Ejecutar OCRmyPDF
    subprocess.run(
        [
            "ocrmypdf",
            "--language", LANG,
            "--force-ocr",
            # "--skip-text",
            str(pdf_path),
            str(ocr_pdf_path)
        ],
        check=True
    )
    ### NOTA: 
    # --force-ocr
    # Fuerza OCR incluso si el PDF ya tiene texto
    # --skip-text
    # Si el PDF ya tiene texto, no hace OCR
    # --redo-ocr
    # Rehacer OCR si detecta texto previo
    # 🔴 Son mutuamente excluyentes porque representan decisiones opuestas.


    # Extraer texto
    text_pages = []
    with pdfplumber.open(ocr_pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text_pages.append({
                "page": i + 1,
                "text": page.extract_text() or ""
            })

    return {
        "file": pdf_path.name,
        "type": "pdf_scanned",
        "pages": len(text_pages),
        "raw_text": text_pages,
        "note": "Texto extraído con OCRmyPDF"
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
        "raw_text": text
    }

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
# Main
# -----------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []

    files = sorted(DOCS_DIR.iterdir())

    if not files:
        print("⚠️  No hay archivos en /docs")
        return

    for file_path in files:
        try:
            print(f"📄 Procesando: {file_path.name}")

            if is_pdf(file_path):
                result = ocr_pdf(file_path)

            elif is_image(file_path):
                result = ocr_image(file_path)

            else:
                print(f"⏭️  Formato no soportado: {file_path.name}")
                continue

            results.append(result)

        except Exception as e:
            print(f"❌ Error procesando {file_path.name}: {e}")
            results.append({
                "file": file_path.name,
                "error": str(e)
            })

    # Guardar JSON
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ OCR finalizado. Resultado en: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()


