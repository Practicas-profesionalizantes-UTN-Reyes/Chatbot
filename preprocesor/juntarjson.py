import json

# Archivos originales

output_path = "data/embe/jsonjuntos.json"

def juntar_json(json1_path,json2_path):
    with open(json1_path, "r", encoding="utf-8") as f:
        data1 = json.load(f)

    # Cargar el segundo
    with open(json2_path, "r", encoding="utf-8") as f:
        data2 = json.load(f)

    # Calcular offset (último id del primero)
    offset = max(item["id"] for item in data1)

    # Ajustar ids del segundo
    for item in data2:
        item["id"] += offset

    # Unir
    data_final = data1 + data2

    # Guardar
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_final, f, indent=2, ensure_ascii=False)
