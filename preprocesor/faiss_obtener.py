import faiss
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer , util


modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')


def crear_indices_faiss(chunks_json, path):
    """
    chunks_json: archivo JSON con lista de dicts [{"id": ..., "texto": ...}, ...]
    path: carpeta donde guardar index.faiss y referencias.json
    """
    os.makedirs(path, exist_ok=True)

    with open(chunks_json, "r", encoding="utf-8") as f:
        data = json.load(f)  # data es lista de dicts

    textos = [str(d["texto"]) for d in data]
    ids = [d["id"] for d in data]


    embeddings = modelo.encode(textos, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(path, "index.faiss"))

    # Guardar referencias aparte para no pisar jsonjuntos.json
    referencias = [{"id": id_num, "texto": txt} for id_num, txt in zip(ids, textos)]
    with open(os.path.join(path, "referencias.json"), "w", encoding="utf-8") as f:
        json.dump(referencias, f, indent=2, ensure_ascii=False)


def buscar_similares(consulta: str, indice_path, top_k=3):
    index = faiss.read_index(os.path.join(indice_path, "index.faiss"))

    with open(os.path.join(indice_path, "referencias.json"), "r", encoding="utf-8") as f:
        referencias = json.load(f)

    emb = modelo.encode([consulta], convert_to_numpy=True)
    distancias, indices = index.search(emb, top_k)

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
    emb_nueva = modelo.encode(pregunta, convert_to_tensor=True)

    with open("./data/output/respuestas.json", "r", encoding="utf-8") as f:
        referencias = json.load(f)

    mejor_sim = 0
    mejor_resp = None

    for q, resp in referencias.items():
        # Generar embedding de la pregunta guardada
        emb_guardado = modelo.encode(q, convert_to_tensor=True)

        # Similaridad
        sim = util.pytorch_cos_sim(emb_guardado, emb_nueva).item()

        if sim > mejor_sim:
            mejor_sim = sim
            mejor_resp = resp

    if mejor_sim >= 0:
        return mejor_resp
    return None

