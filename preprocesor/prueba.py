import faiss
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from llama_cpp import Llama

# ==============================
# Cargar modelo de IA (llama.cpp)
# ==============================
llm = Llama(
    model_path="preprocesor/openhermes-2.5-mistral-7b.Q4_K_M.gguf",  # tu modelo local
    n_ctx=8192,   # tokens de contexto
    n_threads=6,
    verbose=False
)

# ==============================
# Modelo de embeddings (offline)
# ==============================
modelo = SentenceTransformer('multi-qa-MiniLM-L6-cos-v1')


# ==============================
# Función: buscar en FAISS
# ==============================
def buscar_similares(consulta: str, indice_path, top_k=3):
    index = faiss.read_index(os.path.join(indice_path, "index.faiss"))

    with open(os.path.join(indice_path, "jsonjuntos.json"), "r", encoding="utf-8") as f:
        referencias = json.load(f)
    
    emb = modelo.encode([consulta], convert_to_numpy=True)

    distancias, indices = index.search(emb, top_k)

    print("Indices devueltos por FAISS:", indices)
    print("Distancias:", distancias)
    print("Cantidad de referencias en JSON:", len(referencias))

    resultados = []
    for i, idx in enumerate(indices[0]):
        print(">> Evaluando idx:", idx)  # DEBUG
        if 0 <= idx < len(referencias):
            chunk = referencias[idx]
            texto = " ".join(chunk["texto"]) if isinstance(chunk["texto"], list) else chunk["texto"]
            resultados.append(texto)
        else:
            print("❌ idx fuera de rango:", idx)

    return resultados



# ==============================
# Función: pedir consulta al modelo
# ==============================
def pedir_consulta(consul, chunks):
    contexto = "\n\n".join([f"Fragmento {i+1}:\n{c}" for i, c in enumerate(chunks)])

    prompt = f"""
    Respondé únicamente usando los siguientes fragmentos de contexto.
    Si la respuesta no está en ellos, decí: "No sé la respuesta con la información provista."

    Contexto:
    {contexto}

    Pregunta: {consul}
    Respuesta:
    """

    print("==== PROMPT ENVIADO ====")
    print(prompt)
    print("========================")

    output = llm(
        prompt,
        max_tokens=500,
        echo=False,
        stop=["Pregunta:", "CONTEXT START", "CONTEXT END"]
    )

    return output["choices"][0]["text"].strip()


# ==============================
# MAIN de prueba
# ==============================

consulta = "¿Para que usamos las cookies?"

# Buscar en embeddings locales
resultados = buscar_similares(consulta, "data/embeddings", top_k=5)

# Pasar al modelo
respuesta = pedir_consulta(consulta, resultados)

print("\n\nRespuesta generada:")
print(respuesta)

del llm