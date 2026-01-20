VER DIRECTAMENTE: ## Build de la imagen
VER DIRECTAMENTE: ##  Run del contenedor con volumen (modo interactivo - Manual - debug) (script desde host - editable)


## Docker: (ETL batch local OCR con OCRmyPDF + Tesseract)
Arranca el contenedor
Ejecuta extract_text.py (automaticamente al encender el contenedor)
Procesa TODO /app/docs
Guarda raw_ocr.json en /app/output
Se apaga


## carpeta real en WSL:
```
~/mydocker/my001script_ocr
```

## 📁 Estructura final del proyecto (tal como acordamos)

```text
my001script_ocr/
├── docs/            # PDFs / imágenes de entrada (montado como volumen)
├── output/          # JSON de salida
├── /
│   └── extract_text.py   # (lo hacemos en la próxima iteración)
├── requirements.txt
│   Uso `opencv-python-headless` para evitar problemas gráficos en Docker.
├── Dockerfile
└── .gitignore
```


# Creacion de las imágenes Docker
🔌 Volúmenes Docker (clave para tu WSL)

## Build de la imagen
```bash
cd ~/mydocker/my001script_ocr
```
```bash
docker build -t my001-ocr:i0126v1 .
```
### Run con volumen montado (Modo automático al encender el contenedor) (script inmutables en la imagen)

```bash
docker run --rm \
  -v ~/mydocker/my001script_ocr/docs:/app/docs \
  -v ~/mydocker/my001script_ocr/output:/app/output \
  my001-ocr:i0126v1
```
###  Run del contenedor con volumen (modo interactivo - Manual - debug) (script inmutables en la imagen)
Recomendado si no se quiere editar el script (está inmutable dentro de la imagen)
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


### Mapeo de volúmenes Docker
Ruta en contenedor
/app/scripts/extract_text.py	❌ Copiado en imagen
-v ~/ruta/local:/app/scripts, cuando se usa estás linea se esta creando un vínculo (bind mount). El contenedor "tapa" la carpeta /app/scripts que existía internamente con el contenido de tu computadora. CUIDADO
-v ~/mydocker/my001script_ocr/docs:/app/docs \ 	✅ Volumen desde WSL
-v ~/mydocker/my001script_ocr/output:/app/output \	✅ Volumen desde WSL
Esta imagen es en su logica:
Estática
Inmutable
Solo lectura
_____________ En producción NO montas código, montas datos. ______________

_################################# RECOMENDADO PARA DESARROLLO #################################_
##  Run del contenedor con volumen (modo interactivo - Manual - debug) (script desde host - editable)
Entrar al contenedor (modo debug - dev) sin rebuild de la imagen para editar el script desde host
```bash
docker run -it --rm \
  -v ~/mydocker/my001script_ocr/scripts:/app/scripts \
  -v ~/mydocker/my001script_ocr/docs:/app/docs \
  -v ~/mydocker/my001script_ocr/output:/app/output \
  my001-ocr:i0126v1 \
  bash
```
Y ya dentro del contenedor correr el script manualmente: (en este caso)
```bash
$ python scripts/extract_text.py
```
Si esta conforme con los cambios en el script, puede
#### Actualizar la imagen (Lo ideal para producción/portabilidad)
Una vez que tu script funcione perfectamente y no quieras tocarlo más, debes "persistirlo" dentro de la imagen (pues esta fue la idea inicial, ver dockerfile).
Ejecutar de nuevo el comando de construcción:
```bash
$ docker build -t my001-ocr:i0126v1 .
```

## Nota importante sobre carpetas vacías y Git
Git no guarda carpetas vacías.
Si quieres que Git mantenga la estructura de carpetas (docs/ y output/) aunque estén vacías, debes crear un archivo vacío dentro de cada una (por convención, se suele usar .gitkeep).
Sugerencia: Crea estos archivos vacíos para que Git mantenga la estructura:

```bash
touch docs/.gitkeep
touch output/.gitkeep
```

# 📄 Nota sobre el proyecto OCR local con Docker


* PDFs/imágenes en `docs/`
* El contenedor los procesa
* El JSON queda en `output/`

* ✅ **OCRmyPDF usa Tesseract internamente**, pero:
  * Detecta PDFs escaneados
  * Maneja rotación
  * Respeta páginas
* ✅ Todo es **local**
* ✅ Docker portable (WSL, Linux, servidor)
* ✅ Separación clara:
  * Infraestructura ✔
  * OCR ✔
  * Normalización ❌ (aún no)










