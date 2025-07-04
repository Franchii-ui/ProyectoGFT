# VideoTranscriber – Transcripción de Video a Texto con LLM

![Estado](https://img.shields.io/badge/Estado-Desarrollo-blue)
![Backend](https://img.shields.io/badge/Backend-Python%20%7C%20FastAPI-green)
![Frontend](https://img.shields.io/badge/Frontend-Astro%20%7C%20TypeScript-orange)
![Última actualización](https://img.shields.io/badge/Actualizado-2025--06--24-informational)

---

## Descripción Técnica

**VideoTranscriber** es una plataforma web para la transcripción automática de video a texto utilizando modelos LLM (Large Language Models). El sistema implementa una arquitectura desacoplada y escalable, permitiendo el procesamiento eficiente y la administración de archivos audiovisuales.

---

## Arquitectura General

- **Frontend:**  
  - Framework: [Astro](https://astro.build/)  
  - Lenguajes: TypeScript, HTML5, CSS3  
  - UI: Componentes reutilizables, renderizado híbrido (SSG + islas interactivas), integración directa con la API

- **Backend:**  
  - Lenguaje: Python 3.9+
  - Framework principal: [FastAPI](https://fastapi.tiangolo.com/)
  - API RESTful documentada automáticamente (Swagger/OpenAPI)
  - Procesamiento asíncrono: Uvicorn, BackgroundTasks, threading
  - Validaciones estrictas con Pydantic
  - Rutas modularizadas (`/api/v1/videos`, `/api/v1/transcriptions`, etc.)

- **Procesamiento y Almacenamiento:**  
  - Extracción de audio con FFmpeg
  - Preprocesamiento: normalización, segmentación en chunks
  - Modelos LLM conectados vía API (ej: OpenAI Whisper, HuggingFace)
  - Almacenamiento: Local, S3 o configuraciones híbridas
  - Base de datos relacional (ej: PostgreSQL) operada por ORM (SQLAlchemy, Tortoise)

---

## Estructura de Carpetas

```
ProyectoGFT/
│
├── backend/
│   ├── api/                # Routers FastAPI (videos, transcriptions, users)
│   ├── core/               # Configuración global, utilidades
│   ├── models/             # ORM y Pydantic Models
│   ├── services/           # Lógica de negocio, integración LLM, procesamiento
│   ├── db/                 # Sesiones, migraciones y seeds
│   ├── main.py             # Punto de entrada de la app FastAPI
│   └── config.py           # Configuración centralizada (Pydantic Settings)
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/     # Componentes Astro
│       ├── layouts/        # Layouts generales
│       └── pages/          # Rutas y vistas
│
├── scripts/                # Scripts CLI, migraciones
├── docs/                   # Documentación técnica
└── .env.example            # Variables de entorno de ejemplo
```

---

## Instalación y Ejecución

### Prerrequisitos

- **Backend:** Python 3.9+ y FFmpeg instalado en el sistema  
- **Frontend:** Node.js 18+ y npm

### Instalación de FFmpeg

#### En **macOS**

Recomendado con [Homebrew](https://brew.sh):

```bash
brew install ffmpeg
```

Verifica la instalación:

```bash
ffmpeg -version
```

#### En **Windows**

1. Ve a la página oficial: https://ffmpeg.org/download.html  
   o descarga directamente desde [gyan.dev](https://www.gyan.dev/ffmpeg/builds/).

2. Descarga el archivo ZIP de la última versión "Release build".

3. Extrae el ZIP en una carpeta, por ejemplo: `C:\ffmpeg`

4. Agrega la carpeta `C:\ffmpeg\bin` a la variable de entorno `PATH`:
   - Busca "Editar las variables de entorno del sistema" en el menú Inicio.
   - En "Variables del sistema", selecciona `Path` y haz clic en "Editar".
   - Agrega una nueva entrada: `C:\ffmpeg\bin`
   - Acepta los cambios y reinicia tu terminal.

5. Verifica la instalación ejecutando en la terminal/cmd:

```cmd
ffmpeg -version
```

---

### Variables de entorno

Completa el archivo `.env` en la raíz del backend, solo se necesita la API Key de OpenAI:

```env
OPENAI_API_KEY=clave_de_la_API (la proporcionaré por correo)
```

---

### Instalación Backend

> **⚠️ Importante:**  
> Antes de ejecutar estos comandos, asegúrate de estar ubicado en la carpeta correcta (`backend`).  
> Recuerda la ruta exacta porque la necesitarás más adelante al iniciar el servidor local.

```bash
cd backend
python -m venv venv
source venv/bin/activate           # En Windows: venv\Scripts\activate
pip install -r requirements.txt
# Asegúrate de tener la base de datos configurada y migrada
```

### Instalación Frontend

> **⚠️ Importante:**  
> Antes de ejecutar estos comandos, asegúrate de estar ubicado en la carpeta correcta (`frontend`).  
> Recuerda la ruta exacta porque la necesitarás más adelante al iniciar el servidor local.

```bash
cd frontend
npm install
```
### Configuración de la base de datos PostgreSQL

Antes de ejecutar la aplicación, asegúrate de que tienes PostgreSQL instalado y en funcionamiento en tu entorno local.

Para crear la base de datos y configurar el usuario según la conexión utilizada en el proyecto (`db.py`), puedes ejecutar los siguientes comandos en tu terminal o en el cliente psql de PostgreSQL:

```bash
# 1. Accede al intérprete de comandos de PostgreSQL como superusuario (puede pedir contraseña):
psql -U postgres

# 2. Crea la base de datos:
CREATE DATABASE franchi;

# 3. (Opcional, si el usuario no existe) Asegúrate de que el usuario 'postgres' tiene la contraseña adecuada:
ALTER USER postgres WITH PASSWORD '12345678';

# 4. Da todos los permisos sobre la base de datos al usuario:
GRANT ALL PRIVILEGES ON DATABASE franchi TO postgres;

# 5. Sal del intérprete de PostgreSQL:
\q
```

La cadena de conexión que utiliza la aplicación es:

```
postgresql+asyncpg://postgres:12345678@localhost:5432/franchi
```

> **Nota:**  
> Si ya tienes otro usuario configurado diferente de `postgres`, puedes adaptar estos comandos según tu configuración.  
> Recuerda que, por seguridad, lo ideal es usar una contraseña más robusta en producción y restringir los permisos del usuario.

---

### Troubleshooting: Problemas comunes al instalar y ejecutar la app

**Error:** No module named 'fastapi'  
**Solución:**  
Asegúrate de haber instalado las dependencias en el entorno virtual correcto:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

**Usar python 3.12 en vez de 3.13**  
**Síntoma:** Errores de compilación al instalar dependencias como `asyncpg` o `pydantic-core`.  
**Solución:**  
Verifica la versión de Python:
```bash
python --version
# Debe mostrar Python 3.12.x
```
Si no, selecciona la versión correcta (por ejemplo, usando pyenv):
```bash
pyenv install 3.12.11
pyenv local 3.12.11
```
Luego, crea y activa el entorno virtual de nuevo.

---

**Error al instalar dependencias con pip**  
**Síntoma:** Errores como `Failed building wheel for asyncpg` o `pydantic-core`.  
**Solución:**  
Asegúrate de usar Python 3.12 y pip actualizado:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

**El comando uvicorn no se encuentra o usa la versión incorrecta**  
**Solución:**  
Asegúrate de activar el entorno virtual antes de ejecutar uvicorn:
```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

---

**¿Cómo saber si estoy en el entorno virtual correcto?**  
Cuando actives el entorno virtual, tu terminal debe mostrar el nombre del entorno al inicio de la línea, por ejemplo (esto depende de la ruta donde hayas clonado el repositorio):
```
(.venv) user@macbook proyecto %
```

---

**Consejo:**  
Siempre activa el entorno virtual antes de instalar dependencias o ejecutar la app.  
Si tienes problemas con versiones de Python, considera usar `pyenv` para gestionar varias versiones fácilmente.

---

### Ejecución en desarrollo

> **⚠️ Importante:**  
> - Asegúrate de ejecutar los comandos desde las carpetas correctas:  
>   - `backend` para el servidor FastAPI  
>   - `frontend` para Astro  
> - El backend (Uvicorn) **debe ejecutarse en el puerto 8000** para que el frontend pueda comunicarse correctamente con la API.
> - Si cambias alguna ruta o puerto, actualízalo también en la configuración y en las variables de entorno (`.env`) de ambos proyectos.

En dos terminales diferentes:

```bash
# Terminal 1: Backend (FastAPI)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend (Astro)
cd frontend
npm run dev
```

- Acceso Frontend: http://localhost:4321  
- API Docs (Swagger): http://localhost:8000/docs  
- Health: http://localhost:8000/health

---

## Flujo Básico de Uso

1. **Carga de Video:**  
   El usuario sube un archivo soportado (`mp4`, `avi`, `mkv`, etc) vía frontend.  
   El backend valida formato/tamaño y almacena temporalmente.

2. **Procesamiento:**  
   - Extracción y segmentación de audio.
   - Envío de chunks al LLM para transcripción paralela/asíncrona.
   - Agregación, postprocesado y almacenamiento de la transcripción.

3. **Consulta y Exportación:**  
   - El usuario visualiza el avance en tiempo real.
   - Puede descargar la transcripción en TXT, SRT, JSON, etc.

---

## Endpoints Principales (API REST FastAPI)

| Endpoint            | Método | Descripción                                    |
|---------------------|--------|------------------------------------------------|
| `/api/v1/videos`    | POST   | Subida de video                                |
| `/api/v1/videos`    | GET    | Listado de videos del usuario                  |
| `/api/v1/videos/{id}` | GET  | Estado/progreso de procesamiento               |
| `/api/v1/transcriptions/{id}` | GET | Descargar transcripción          |

Documentación Swagger: `/docs`  
Status/Health: `/health`

---

## Pruebas

- **Backend:** Pytest + TestClient de FastAPI.  
- **Frontend:** Vitest/Jest y pruebas E2E con Cypress.

---

## Seguridad

- CORS configurado solo para orígenes permitidos.
- Validación exhaustiva de archivos y datos de entrada.
- Logs centralizados y manejo de errores global.
- **Nota:** Actualmente no está implementada autenticación JWT/OAuth.

---

## Mantenimiento y Escalabilidad

- Modularidad estricta para facilitar refactoring y pruebas.
- Soporte para despliegue en Docker/Kubernetes.
- Listo para integración continua (GitHub Actions).
- Escalabilidad horizontal via workers asíncronos.

---

## Autor

**Franchii-ui**  
Última actualización: 2025-06-24 10:52:26 UTC

---
