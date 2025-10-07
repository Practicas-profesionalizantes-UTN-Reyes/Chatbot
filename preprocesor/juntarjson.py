import json

# Archivo de salida donde se guardará el JSON combinado
output_path = "data/embe/jsonjuntos.json"

def juntar_json(json1_path, json2_path):
    """
    Une dos archivos JSON que contienen listas de diccionarios con un campo "id".
    Ajusta los IDs del segundo archivo para que no se repitan.
    
    json1_path: ruta del primer archivo JSON
    json2_path: ruta del segundo archivo JSON
    """
    # Cargar primer archivo
    with open(json1_path, "r", encoding="utf-8") as f:
        data1 = json.load(f)

    # Cargar segundo archivo
    with open(json2_path, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    # Calcular offset = último id del primer archivo
    offset = max(item["id"] for item in data1)

    # Ajustar IDs del segundo archivo para que sean únicos
    for item in data2:
        item["id"] += offset

    # Unir ambos conjuntos de datos
    data_final = data1 + data2

    # Guardar resultado en el archivo de salida
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=2, ensure_ascii=False)
