# 🤖 Alura Agente - BimBam Buy

¡Bienvenido al proyecto final **Alura Agente**! Este repositorio contiene un Asistente Virtual Inteligente (IA) diseñado para **BimBam Buy**, una empresa de comercio electrónico.

## 🎯 Objetivo del Proyecto

El objetivo es resolver un problema común: la pérdida de tiempo buscando información dentro de múltiples manuales, políticas y documentos internos. 
Hemos implementado un sistema **RAG (Retrieval-Augmented Generation)** que lee una colección completa de archivos **PDF**, los procesa y permite a los colaboradores y clientes hacer preguntas en lenguaje natural para obtener respuestas directas y precisas.

## ⚙️ Tecnologías Utilizadas

- **Python**: Lenguaje base del proyecto.
- **LangChain**: Herramienta de orquestación del flujo RAG (cargadores de documentos `PyPDFDirectoryLoader`, splitters y cadenas de recuperación).
- **Google Generative AI (Gemini)**: Utilizamos la API más moderna con el modelo `gemini-2.5-flash` para generación de texto y `gemini-embedding-001` para embeddings.
- **FAISS**: Base de datos vectorial local para realizar búsquedas de similitud ultrarrápidas sin costos adicionales de alojamiento.
- **Flask**: Servidor web ligero que provee el backend de nuestra interfaz.
- **HTML/CSS/JS (Vainilla)**: Interfaz de chat estilo "premium e-commerce", con soporte para renderizado de texto estructurado en Markdown (mediante `marked.js`).

## 🏗️ Arquitectura del Sistema

1. **Ingesta de Datos (`document_processor.py`)**: 
   - Escanea todos los archivos PDF presentes en el directorio `/data`.
   - Divide el contenido en fragmentos (chunks) usando `RecursiveCharacterTextSplitter` optimizado para no exceder los límites de cuota de la API gratuita.
   - Convierte el texto en vectores de conocimiento y los almacena en una base de datos local `faiss_index`.
2. **Motor de Inferencia (`agent.py`)**: 
   - Carga la base de datos y prepara el LLM (Gemini).
   - Recibe la pregunta del usuario, busca los fragmentos relevantes y genera una respuesta natural y bien formateada basada **únicamente** en la información interna de BimBam Buy.
3. **Interfaz Gráfica (`app.py`)**: 
   - Levanta el servidor Flask.
   - Presenta una UI moderna con avatares, diseño responsive, burbujas de chat, micro-animaciones y soporte para Markdown.

## 🚀 Guía de Instalación y Uso Local

### 1. Requisitos Previos
- Instalar Python (probado en entornos 3.11 hasta 3.14).
- Conseguir una API Key gratuita desde [Google AI Studio](https://aistudio.google.com/).

### 2. Configurar Entorno
```bash
# 1. Clona este repositorio y entra a la carpeta
git clone <URL-DEL-REPO>
cd alura-agente

# 2. Crea y activa tu entorno virtual
python -m venv venv
source venv/bin/activate  # (En Windows: venv\Scripts\activate)

# 3. Instala todas las dependencias
pip install -r requirements.txt

# 4. Configura tu credencial de seguridad
cp .env.example .env
# --> Abre el archivo .env y pega tu GOOGLE_API_KEY
```

### 3. Procesar los Manuales y Políticas
Asegúrate de que tus archivos PDF estén dentro de la carpeta `data/`.
```bash
python document_processor.py
```
*(Esto procesará las páginas, consultará la API de Google y guardará la base de datos `faiss_index` en la raíz del proyecto).*

### 4. Iniciar el Chat Inteligente
```bash
python app.py
```
Ingresa a **`http://127.0.0.1:7860`** en tu navegador. 

## 💡 Ejemplos de Preguntas Soportadas
- 📦 *¿Cuántos días tengo para devolver un producto dañado?*
- ✈️ *¿Hacen envíos internacionales y cuáles son los costos?*
- 🤝 *¿Cómo funciona el programa de afiliados y cómo me registro?*

## 🛠️ Solución de Problemas (Troubleshooting)

- **Errores de Metaclases con Protobuf**: El proyecto maneja automáticamente incompatibilidades recientes de Python 3.14 forzando el uso de `PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION="python"`.
- **Límites de Cuota (429 Resource Exhausted)**: Si cargas miles de páginas, Google puede frenar las consultas gratuitas de Embedding. El procesador fue optimizado (`chunk_size=4000`) para minimizar este problema. Si ocurre, espera 1 minuto y vuelve a intentarlo.
- **"Falta configurar GOOGLE_API_KEY"**: Recuerda que las claves actuales de Gemini siempre deben comenzar con las letras `AIza...`.

## 🌐 Siguiente Paso: Despliegue en la Nube
El proyecto está completamente listo para ser llevado a producción. Para esto, se recomienda instanciar un servidor Ubuntu en **Oracle Cloud Infrastructure (OCI)**, clonar este repositorio, instalar dependencias, ejecutar el procesador y exponer el puerto `7860` a la red pública.

---
*Desarrollado como parte del Desafío Final de Alura.*
