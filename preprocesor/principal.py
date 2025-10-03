import hashlib                                  #CONSULTA CON LO NUEVO EN LINEA 214
import os
import pickle
import re
import pprint
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer

# Local imports
from Main_formatear import crear_embeddings
from juntarjson import juntar_json
from faiss_obtener import buscar_similares, crear_indices_faiss, Respuesta_rapida

# ============================
# CONFIGURATION
# ============================
class Config:
    DATA_INPUT = Path("./data/imputPDF")
    HASH_FILE = Path("./data/cifrado/file_hashes.pkl")
    EMBE_PATH = Path("./data/embe")
    OUTPUT_PATH = Path("./data/output")
    EMBEDDINGS_PATH = Path("./data/embeddings")
    MODEL_NAME = 'multi-qa-MiniLM-L6-cos-v1'
    SIMILARITY_THRESHOLD = 0.7
    MIN_SIMILARITY_FILTER = 0.35
    TOP_N_FILTER = 5
    FAISS_TOP_K = 5

# Initialize model once
modelo = SentenceTransformer(Config.MODEL_NAME)

# ============================
# AUXILIARY FUNCTIONS
# ============================
def calcular_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def cargar_hash_archivo() -> Dict[str, str]:
    """Load saved file hashes."""
    if Config.HASH_FILE.exists():
        try:
            with open(Config.HASH_FILE, "rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, FileNotFoundError):
            return {}
    return {}

def guardar_hash(hash_dict: Dict[str, str]) -> None:
    """Save file hashes."""
    Config.HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(Config.HASH_FILE, "wb") as f:
        pickle.dump(hash_dict, f)

def hay_archivos_nuevos() -> Tuple[bool, List[str], List[str]]:
    """Check for new, modified, or deleted files."""
    archivos_actuales = {}
    for archivo in Config.DATA_INPUT.iterdir():
        if archivo.is_file():
            archivos_actuales[archivo.name] = calcular_hash(archivo)

    hashes_cargados = cargar_hash_archivo()

    nuevos_o_cambiados = [
        archivo for archivo, h in archivos_actuales.items()
        if archivo not in hashes_cargados or hashes_cargados[archivo] != h
    ]
    eliminados = [archivo for archivo in hashes_cargados if archivo not in archivos_actuales]

    if nuevos_o_cambiados or eliminados:
        guardar_hash(archivos_actuales)
        return True, nuevos_o_cambiados, eliminados
    
    return False, [], []

def vaciar_carpeta(path_carpeta: Path) -> None:
    """Empty a folder safely."""
    if not path_carpeta.exists():
        return
        
    for item in path_carpeta.iterdir():
        try:
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                vaciar_carpeta(item)
                item.rmdir()
        except (PermissionError, OSError) as e:
            print(f"Warning: Could not delete {item}: {e}")

def normalizar_texto(texto: Any) -> str:
    """Normalize text input."""
    if isinstance(texto, list):
        return " ".join(map(str, texto))
    return str(texto).strip()

# ============================
# EMBEDDINGS + FAISS
# ============================
def cargar_nuevos_embeddings() -> None:
    """Generate new embeddings and create FAISS index."""
    # Clean output directories
    vaciar_carpeta(Config.OUTPUT_PATH)
    vaciar_carpeta(Config.EMBEDDINGS_PATH)

    # Generate individual embeddings
    for archivo in Config.DATA_INPUT.iterdir():
        if archivo.is_file():
            crear_embeddings(str(archivo))

    # Combine JSONs
    data_folder = Config.EMBEDDINGS_PATH
    json_files = list(data_folder.glob("*.json"))
    
    if not json_files:
        print("No JSON files found for processing")
        return

    # Process JSON files sequentially
    final_json = Config.EMBE_PATH / "jsonjuntos.json"
    
    if len(json_files) >= 2:
        # Start with first two files
        juntar_json(str(json_files[0]), str(json_files[1]))
        
        # Merge remaining files
        for json_file in json_files[2:]:
            juntar_json(str(final_json), str(json_file))
    elif json_files:
        # Only one file - copy it to final location
        import shutil
        shutil.copy2(str(json_files[0]), str(final_json))

    # Create FAISS index
    crear_indices_faiss(str(final_json), str(Config.EMBE_PATH))

def filtrar_por_similitud(pregunta: str, texto: str, modelo_embed: SentenceTransformer, 
                         min_sim: float = Config.MIN_SIMILARITY_FILTER, 
                         top_n: int = Config.TOP_N_FILTER) -> str:
    """Filter text by similarity to the question."""
    if not texto.strip():
        return texto
        
    # Split text into meaningful parts
    partes = re.split(r'(?<=[.!?])\s+', texto)
    if len(partes) <= 1:
        partes = texto.split(". ")
    
    # Encode question and text parts
    emb_q = modelo_embed.encode([pregunta])[0]
    emb_parts = modelo_embed.encode(partes)

    # Calculate similarities
    sims = []
    for e, p in zip(emb_parts, partes):
        norm_e = np.linalg.norm(e)
        norm_q = np.linalg.norm(emb_q)
        if norm_e > 0 and norm_q > 0:  # Avoid division by zero
            similarity = np.dot(emb_q, e) / (norm_q * norm_e)
            sims.append((similarity, p))

    # Filter and sort by similarity
    filtered_sims = [s for s in sims if s[0] >= min_sim]
    filtered_sims.sort(key=lambda x: x[0], reverse=True)

    if filtered_sims:
        return " ".join([p for _, p in filtered_sims[:top_n]])
    
    return texto

# ============================
# MAIN QUERY FUNCTION (Para Telegram)
# ============================
def responder_a_consulta(consulta: str) -> str:
    if Respuesta_rapida(consulta):
        resultado = Respuesta_rapida(consulta)
        """Main function to respond to a query."""
    else:
        resultado = "Por favor, proporciona una consulta válida."
        return resultado
    
    return resultado


