import faiss
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from ModeloIA import pedir_consulta

modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')


def crear_indices_faiss(chunks,path):     #algo/algo2/    chunks es la direccion del .json que contiene los chunks
   
    with open(chunks, "r", encoding = "utf-8") as f:
        data = json.load(f)

    ordenado = sorted(data.items(), key=lambda x: int(x[0]))

    ids = [int(k) for k, _ in ordenado]
    textos = [v for _, v in ordenado]

    embeddings = modelo.encode(textos, convert_to_numpy=True)    

    dim = embeddings.shape[1]        #Obtiene la cantidad de columnas(dimension del vector)
    index = faiss.IndexFlatL2(dim)  #Indice plano con distancia L2 (Euclidea), dim es para las dimension de cada vector
    index.add(embeddings)   #Agrega todos los vectores(uno por chunk) al FAISS

    faiss.write_index(index, os.path.join(path,"index.faiss")) #algo/algo2/index.faiss

    referencias = [{"id": id_num, "texto": txt} for id_num, txt in zip(ids, textos)]

    with open(os.path.join(path,"textos.json"), "w", encoding="utf-8") as f:
        json.dump(referencias,f , indent=2, ensure_ascii = False)


def buscar_similares(consulta : str, indice_path, top_k=3):

    index = faiss.read_index(os.path.join(indice_path,"index.faiss"))

    with open(os.path.join(indice_path,"textos.json"),"r", encoding="utf-8") as f:
        referencias = json.load(f)
    
    emb = modelo.encode([consulta], convert_to_numpy=True)

    distancias, indices = index.search(emb,top_k)     #faiss.IndexFlatL2(dim)

    resultados = []

    for i, idx in enumerate(indices[0]):
        chunk = referencias[idx]
        resultados.append({
            "id":chunk["id"],
            "texto": chunk["texto"],
            "distancia": float(distancias[0][i])
        })
    
    return resultados

consulta="inteligencia"
Respuesta=(buscar_similares(consulta, "data/embeddings", top_k=10))
#contexto = "\n".join(r["texto"]for r in Respuesta)

resultado_final=pedir_consulta(consulta,Respuesta)
print("Respuesta generada:")
print(resultado_final)

