# Chatbot

#Roadmap del Proyecto: Chatbot con LLaMA + Telegram

---

## Objetivo General del Proyecto

Desarrollar un **chatbot local** que responda preguntas a partir de información extraída de:

- Archivos PDF
- Sitios web específicos

El bot utilizará un modelo **LLaMA local** (`llama-cpp`) y responderá por **Telegram**.

---

## Fases del Proyecto

1. **Web Scraping**  
   Extracción de contenido útil desde sitios web definidos.

2. **Preprocesamiento del Texto**  
   Limpieza sin deformar, eliminación de encabezados/pies, división en *chunks*.

3. **Generación de Embeddings**  
   Transformar cada chunk en vectores semánticos (`sentence-transformers`).

4. **Almacenamiento Vectorial (FAISS)**  
   Guardar y buscar chunks relevantes por similitud semántica.

5. **Integración con llama-cpp**  
   Generar respuestas usando un modelo LLaMA local, sin APIs externas.

6. **Conexión con Telegram**  
   Desplegar el bot usando `python-telegram-bot`.

7. **Funciones adicionales**  
   Logs de usuarios, comandos (`/start`, `/help`), carga de PDFs nuevos.

8. **Documentación, pruebas y deploy final**

---

## Glosario de Términos

- **Web Scraping**  
  Técnica para extraer contenido útil del HTML de una web (con `BeautifulSoup`, etc).

- **Chunking**  
  División del texto en fragmentos coherentes más pequeños, para facilitar el análisis y la búsqueda.

- **Embeddings**  
  Representaciones matemáticas de un texto según su significado. Permiten comparar textos.

- **FAISS**  
  Librería para búsquedas rápidas por similitud entre vectores (embeddings).

- **llama-cpp**  
  Motor local que ejecuta modelos LLaMA sin necesidad de usar APIs pagas. Corre en CPU o GPU.

- **Telegram Bot**  
  Bot que responde mensajes automáticamente en Telegram usando código Python.




