import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
import os

# Ruta de embeddings
indice_path = "data/embe"

# Modelo de embeddings (debe ser el mismo que usás en las búsquedas)
modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')

# Leer los chunks
with open(os.path.join(indice_path, "jsonjuntos.json"), "r", encoding="utf-8") as f:
    referencias = json.load(f)

# Convertir textos a embeddings
docs = [" ".join(r["texto"]) if isinstance(r["texto"], list) else r["texto"] for r in referencias]
embs = modelo.encode(docs, convert_to_numpy=True)

# Crear índice FAISS
dim = embs.shape[1]
index = faiss.IndexFlatL2(dim)  # métrica L2 (distancia euclídea)
index.add(np.array(embs))

# Guardar índice
faiss.write_index(index, os.path.join(indice_path, "index.faiss"))

print(f"✅ Nuevo índice creado con {len(referencias)} documentos")
