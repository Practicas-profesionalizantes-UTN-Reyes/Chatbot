import json
import re
import argparse
from pathlib import Path

def cargar_texto(path_txt) -> str:
    """
    Carga el texto de un archivo .txt
    - Expande "~" si existe
    - Verifica que el archivo exista
    - Lee el contenido en UTF-8
    """
    p = Path(path_txt).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"No existe el archivo: {p}")
    return p.read_text(encoding="utf-8", errors="replace")


def normalizar_texto(raw: str) -> str:
    """
    Limpia y normaliza un texto:
    - Uniformiza saltos de línea
    - Elimina espacios extras
    - Une preguntas que estaban partidas en varias líneas
    """
    # Unificar saltos de línea
    txt = raw.replace("\r\n", "\n").replace("\r", "\n")

    # Eliminar espacios iniciales/finales en cada línea
    txt = "\n".join(line.strip() for line in txt.split("\n"))

    # Reemplazar tabulaciones o espacios múltiples por uno solo
    txt = re.sub(r"[\t] {2,}", " ", txt)

    # Procesar preguntas que están divididas en líneas distintas
    lineas = txt.split("\n")
    pegadas = []
    linea_buffer = ""

    for line in lineas:
        if line.startswith("¿"):   # Nueva pregunta detectada
            if linea_buffer:
                pegadas.append(linea_buffer.strip())
                linea_buffer = ""
            pegadas.append(line)
        else:   # No empieza con "¿" → puede ser parte de la respuesta
            if line:
                if linea_buffer:
                    linea_buffer += " " + line
                else:
                    linea_buffer = line
            else:
                if linea_buffer:
                    pegadas.append(linea_buffer.strip())
                    linea_buffer = ""
                pegadas.append("")  # Línea en blanco
    if linea_buffer:
        pegadas.append(linea_buffer.strip())

    return "\n".join(pegadas).strip()


def Hacer_Json(raw: str) -> str:
    """
    Convierte un texto normalizado en un JSON de preguntas/respuestas.
    - Detecta preguntas por el formato "¿...?"
    - Guarda un diccionario {pregunta: respuesta} en respuestas.json
    """
    partes = re.split(r"¿(.*?)\?", raw)

    resultado = {}
    for i in range(1, len(partes), 2):
        pregunta = partes[i].strip()
        respuesta = partes[i+1].strip() if (i+1) < len(partes) else ""
        resultado[pregunta] = respuesta

    with open("./data/output/respuestas.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)


# ======================
# PROCESO PRINCIPAL
# ======================
# 1. Lee el archivo con preguntas en texto plano
# 2. Normaliza el contenido
# 3. Genera un JSON con preguntas y respuestas
Hacer_Json(normalizar_texto(cargar_texto("./data/output/Preguntas_texto.txt")))
