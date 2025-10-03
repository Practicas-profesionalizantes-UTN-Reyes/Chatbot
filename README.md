# Chatbot

# Roadmap del Proyecto: Chatbot con LLaMA + Telegram

---

## Objetivo General del Proyecto

Desarrollar un **chatbot local** que responda preguntas a partir de información extraída de:

- Archivos PDF
- Sitios web específicos

El bot utilizará un modelo **LLaMA local** (`llama-cpp`) y responderá por **Telegram**.

---

## Fases del Proyecto

* . **Web Scraping**  
   Extracción de contenido útil desde sitios web definidos.

* . **Preprocesamiento del Texto**  
   Limpieza sin deformar, eliminación de encabezados/pies, división en *chunks*.

* . **Generación de Embeddings**  
   Transformar cada chunk en vectores semánticos (`sentence-transformers`).

* . **Almacenamiento Vectorial (FAISS)**  
   Guardar y buscar chunks relevantes por similitud semántica.

* . **Funciones adicionales**  
   Logs de usuarios, comandos (`/start`, `/help`), carga de PDFs nuevos.

* . **Documentación, pruebas y deploy final**

  --------- A INTEGRAR --------- 

* . **Integración con llama-cpp**  
   Generar respuestas usando un modelo LLaMA local, sin APIs externas.

* . **Conexión con Telegram**  
   Desplegar el bot usando `python-telegram-bot`.

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




