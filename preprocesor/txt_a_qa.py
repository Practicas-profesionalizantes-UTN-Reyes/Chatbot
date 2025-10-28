import json
import re
from pathlib import Path
import fitz  # pip install PyMuPDF

def cargar_pdf(path_pdf) -> str:
    p = Path(path_pdf).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"No existe el archivo: {p}")

    texto = ""
    doc = fitz.open(p)
    for pagina in doc:
        texto += pagina.get_text("text") + "\n"
    doc.close()

    return texto


def normalizar_texto(raw: str) -> str:
    txt = raw.replace("\r\n", "\n").replace("\r", "\n")
    txt = "\n".join(line.strip() for line in txt.split("\n"))
    txt = re.sub(r"[\t] {2,}", " ", txt)

    lineas = txt.split("\n")
    pegadas = []
    linea_buffer = ""

    for line in lineas:
        if line.startswith("¿"):
            if linea_buffer:
                pegadas.append(linea_buffer.strip())
                linea_buffer = ""
            pegadas.append(line)
        else:
            if line:
                if linea_buffer:
                    linea_buffer += " " + line
                else:
                    linea_buffer = line
            else:
                if linea_buffer:
                    pegadas.append(linea_buffer.strip())
                    linea_buffer = ""
                pegadas.append("")
    if linea_buffer:
        pegadas.append(linea_buffer.strip())

    return "\n".join(pegadas).strip()


def extraer_preguntas_respuestas(texto: str) -> dict:
    partes = re.split(r"¿(.*?)\?", texto)
    resultado = {}
    for i in range(1, len(partes), 2):
        pregunta = partes[i].strip()
        respuesta = partes[i+1].strip() if (i+1) < len(partes) else ""
        resultado[pregunta] = respuesta
    return resultado


def procesar_todos_los_pdfs(carpeta_entrada="./data/imputPDF", carpeta_salida="./data/output"):
    entrada_path = Path(carpeta_entrada)
    salida_path = Path(carpeta_salida)
    salida_path.mkdir(parents=True, exist_ok=True)

    todos_resultados = {}

    for pdf_path in entrada_path.glob("*.pdf"):
        print(f"Procesando: {pdf_path.name}")
        texto = normalizar_texto(cargar_pdf(pdf_path))
        preguntas_respuestas = extraer_preguntas_respuestas(texto)
        # Combina los diccionarios (si hay preguntas repetidas, se sobreescriben)
        todos_resultados.update(preguntas_respuestas)

    # Guardar el JSON combinado
    with open(salida_path / "respuestas.json", "w", encoding="utf-8") as f:
        json.dump(todos_resultados, f, ensure_ascii=False, indent=4)
    print(f"JSON generado con {len(todos_resultados)} preguntas en {salida_path/'respuestas.json'}")


# ======================
# EJECUCIÓN PRINCIPAL
# ======================
procesar_todos_los_pdfs()
