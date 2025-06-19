# 🎬 VideoTranscriber

![Estado](https://img.shields.io/badge/Estado-En%20Desarrollo-yellow)
![Versión](https://img.shields.io/badge/Versión-1.0.0-blue)
![Última Actualización](https://img.shields.io/badge/Última%20Actualización-2025--06--19-green)

<p align="center">
  <img src="https://via.placeholder.com/800x400?text=VideoTranscriber+Demo" alt="VideoTranscriber Demo" width="800">
</p>

## 📝 Descripción

VideoTranscriber es una aplicación web avanzada que permite transcribir contenido de video a texto utilizando modelos de lenguaje de gran escala (LLM). Desarrollada para GFT, esta herramienta optimiza flujos de trabajo que requieren extracción de texto a partir de contenido audiovisual.

## ✨ Características Principales

- 🎯 **Transcripción Precisa**: Conversión de audio a texto con alta fidelidad usando modelos LLM
- 🚀 **Procesamiento Rápido**: Optimizado para manejar archivos de video de diversos tamaños
- 🔍 **Identificación de Hablantes**: Capacidad para distinguir entre diferentes voces (opcional)
- 🌐 **Soporte Multilingüe**: Transcribe contenido en múltiples idiomas
- 📊 **Panel de Control**: Interfaz intuitiva para gestionar archivos y transcripciones
- 💾 **Exportación Versátil**: Genera transcripciones en diversos formatos (TXT, SRT, JSON)
- 🔒 **Seguridad Integrada**: Protección de datos y control de acceso por roles

## 🛠️ Tecnologías

### Frontend
- [Astro](https://astro.build/) - Framework web de alto rendimiento
- HTML5, CSS3, JavaScript/TypeScript
- Componentes reutilizables y UI responsiva

### Backend
- [Python](https://www.python.org/) - Lenguaje principal de backend
- [FastAPI](https://fastapi.tiangolo.com/) - Framework API de alto rendimiento
- Procesamiento asíncrono para tareas intensivas

### IA y Procesamiento
- Modelos de Lenguaje de Gran Escala para transcripción
- Procesamiento de audio y video optimizado
- Algoritmos de reconocimiento de voz y análisis lingüístico

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.9+
- Node.js 16+
- FFmpeg

### Configuración

```bash
# Clonar el repositorio
git clone https://github.com/Franchii-ui/ProyectoGFT.git
cd ProyectoGFT

# Configurar el entorno virtual de Python
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Instalar dependencias del frontend
cd frontend
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones
