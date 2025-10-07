import faiss
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer , util

# Se carga el modelo de embeddings (transforma texto en vectores numéricos)
modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')


def crear_indices_faiss(chunks_json, path):
    """
    Genera un índice FAISS a partir de un archivo JSON con chunks de texto.
    
    chunks_json: archivo JSON con lista de dicts [{"id": ..., "texto": ...}, ...]
    path: carpeta donde se guardarán el índice y las referencias
    """
    os.makedirs(path, exist_ok=True)   # crea la carpeta si no existe

    # Leer los datos desde el JSON
    with open(chunks_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Separar textos e IDs
    textos = [str(d["texto"]) for d in data]
    ids = [d["id"] for d in data]

    # Calcular embeddings
    embeddings = modelo.encode(textos, convert_to_numpy=True)

    # Crear índice FAISS
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # Guardar índice en archivo
    faiss.write_index(index, os.path.join(path, "index.faiss"))

    # Guardar referencias (IDs y textos originales)
    referencias = [{"id": id_num, "texto": txt} for id_num, txt in zip(ids, textos)]
    with open(os.path.join(path, "referencias.json"), "w", encoding="utf-8") as f:
        json.dump(referencias, f, indent=2, ensure_ascii=False)


def buscar_similares(consulta: str, indice_path, top_k=3):
    """
    Busca los textos más similares a una consulta dentro del índice FAISS.

    consulta: texto de entrada
    indice_path: ruta donde están "index.faiss" y "referencias.json"
    top_k: cantidad de resultados a devolver
    """
    # Cargar índice
    index = faiss.read_index(os.path.join(indice_path, "index.faiss"))

    # Cargar referencias
    with open(os.path.join(indice_path, "referencias.json"), "r", encoding="utf-8") as f:
        referencias = json.load(f)

    # Embedding de la consulta
    emb = modelo.encode([consulta], convert_to_numpy=True)

    # Buscar en FAISS
    distancias, indices = index.search(emb, top_k)

    # Armar resultados con id, texto y distancia
    resultados = []
    for i, idx in enumerate(indices[0]):
        if 0 <= idx < len(referencias):
            chunk = referencias[idx]
            resultados.append({
                "id": chunk["id"],
                "texto": chunk["texto"],
                "distancia": float(distancias[0][i])
            })
    return resultados


def Respuesta_rapida(pregunta: str):
    """
    Busca rápidamente una respuesta en "respuestas.json"
    comparando embeddings sin usar FAISS.
    """
    emb_nueva = modelo.encode(pregunta, convert_to_tensor=True)

    # Cargar archivo de respuestas
    with open("./data/output/respuestas.json", "r", encoding="utf-8") as f:
        referencias = json.load(f)

    mejor_sim = 0
    mejor_resp = None

    # Comparar con cada pregunta guardada
    for q, resp in referencias.items():
        emb_guardado = modelo.encode(q, convert_to_tensor=True)
        sim = util.pytorch_cos_sim(emb_guardado, emb_nueva).item()

        if sim > mejor_sim:
            mejor_sim = sim
            mejor_resp = resp

    # Devuelve la respuesta más parecida
    if mejor_sim >= 0:
        return mejor_resp
    return None
