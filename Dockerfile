FROM python:3.11-slim

### (OCR local con OCRmyPDF + Tesseract)

# Evita prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    ocrmypdf \
    ghostscript \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el proyecto
COPY . .

# Comando por defecto (placeholder)
CMD ["python", "scripts/extract_text.py"]