import json
import re
import argparse
from pathlib import Path

def cargar_texto(path_txt) -> str:
    p = Path(path_txt).expanduser().resolve()  # ~ y resolución absoluta
    if not p.exists():
        raise FileNotFoundError(f"No existe el archivo: {p}")
    return p.read_text(encoding="utf-8", errors="replace")



def normalizar_texto(raw:str) -> str:
    txt = raw.replace("\r\n","\n").replace("\r","\n")

    txt = "\n".join(line.strip() for line in txt.split("\n"))

    txt =  re.sub(r"[\t] {2,}", " ", txt)

    #Unir una pregunta que esta en lineas distintas
    
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





def Hacer_Json(raw:str) ->str:
    partes = re.split(r"¿(.*?)\?", raw)

    resultado = {}
    for i in range(1, len(partes), 2):
        pregunta = partes[i].strip()
        respuesta = partes[i+1].strip() if (i+1) < len(partes) else ""
        resultado[pregunta] = respuesta

    with open("./data/output/respuestas.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)


Hacer_Json(normalizar_texto(cargar_texto("./data/output/Preguntas_texto.txt")))
