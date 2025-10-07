from chuncks import chunk_palabras_solapado
import os
import json

def hacer_json(direccion_txt, output_json):
    """
    Convierte un archivo de texto en un JSON de chunks (fragmentos).
    
    - Divide el texto en partes usando `chunk_palabras_solapado`
    - Cada fragmento tiene un ID y el texto correspondiente
    - Guarda el resultado en un archivo JSON dentro de la carpeta indicada
    
    direccion_txt: ruta del archivo de texto
    output_json: carpeta de salida para guardar el JSON
    """
    json_list = []

    # Dividir el texto en chunks con solapamiento
    lista = chunk_palabras_solapado(direccion_txt, largo=100, solapamiento=20)

    # Crear lista de diccionarios con ID y texto
    for i, chunks in enumerate(lista, start=1):
        json_list.append({
            "id": i,
            "texto": [chunks]   # el texto se guarda en lista por consistencia
        })

    # Asegurar que la carpeta de salida exista
    os.makedirs(output_json, exist_ok=True)

    # Nombre de archivo de salida = nombre del txt + "_texto.json"
    nombre_archivo = os.path.splitext(os.path.basename(direccion_txt))[0]
    output_path = os.path.join(output_json, f"{nombre_archivo}_texto.json")

    # Guardar lista en JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_list, f, indent=4, ensure_ascii=False)
    
    return json_list
