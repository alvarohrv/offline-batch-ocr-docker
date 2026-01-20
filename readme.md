# Extractor de texto (OCR) para certificados  
Este proyecto procesa certificados en formato PDF (y algunas imágenes) ubicados en `docs/`, extrae su texto (con OCR cuando aplica) y genera un archivo JSON con   el contenido y metadatos.  
  
## Estructura recomendada de `docs/`  
Para mejorar el orden y permitir análisis por institución, se recomienda clasificar los certificados en carpetas por instituto dentro de `docs/`.  
  
Ejemplo:  
  
docs/  
  SENA/  
    certificado_01.pdf  
    certificado_02.pdf  
  Platzi/  
    curso_python.pdf  
  Codigo_Facilito/  
    diplomado_backend.pdf  
  certificado_sin_clasificar.pdf  
  
  
## Campo `institute` (clasificación automática)  
El script agrega la propiedad `institute` a cada documento procesado si el archivo está dentro de una carpeta en `docs/`,  
`institute` toma el nombre de esa carpeta.  
  - El carácter `_` se convierte en espacio.  
  - El nombre se normaliza a formato tipo “Pascal Case” por palabra.  
  - Ejemplo: `Codigo_Facilito/` → `Codigo Facilito`.  
- Si el archivo está suelto directamente en `docs/` (sin carpeta), `institute` será `"undefined"`.  
  
Esto permite filtrar, agrupar y analizar resultados por institución sin necesidad de etiquetar manualmente.  
  
  
## Salida  
  
El resultado se guarda en `output/raw_ocr.json` e incluye, por cada archivo:  
Ej de documento:  
[  
    {  
    "file": "diploma-api.pdf",  
    "type": "pdf_scanned",  
    "pages": 1,  
    "raw_text": [  
      {  
        "page": 1,  
        "text": "Ó Platzi\nCertifica a\nALVARO H. RUIZ V.\nPor participar y aprobar el\nCURSO DE\nCONSUMO DE API REST\nCON JAVASCRIPT\nChristian Van Der Henst S John Freddy Vega\nCOO DE PLATZI CEO DE PLATZI\nCertificación de aprobación online:\nAprobado el 2 de OCTUBRE de 2022\n16 horas de teoría y práctica\nhttps: //platzi.com/O/\nCódigo: 44709700-d9ba-4a4d-ae42-7eed9b1bc848"  
      }  
    ],  
    "note": "Texto extraído con OCRmyPDF",  
    "institute": "Platzi",  
    "path": "PLATZI/diploma-api.pdf"  
  }  
]  
  
# Construcción de la imagen Docker  
Desde la carpeta del proyecto, ejecutar:  
```bash  
 docker build -t my001script-ocr:i0126v1 .  
```  
  
# Correr el contenedor Docker   
Entrar al contenedor (modo debug)  
```bash  
docker run -it --rm \  
  -v ~/mydocker/my001script_ocr/docs:/app/docs \  
  -v ~/mydocker/my001script_ocr/output:/app/output \  
  my001-ocr:i0126v1 \  
  bash  
```  
Y ya dentro del contenedor correr el script manualmente: (en este caso)  
```bash  
$ python scripts/extract_text.py  
```  
  
  
