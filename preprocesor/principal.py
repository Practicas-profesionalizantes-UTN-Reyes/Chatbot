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
    """Clase de configuración con rutas y parámetros globales."""
    DATA_INPUT = Path("./data/imputPDF")            # Carpeta con PDFs de entrada
    HASH_FILE = Path("./data/cifrado/file_hashes.pkl")  # Archivo para guardar hashes
    EMBE_PATH = Path("./data/embe")                 # Carpeta de FAISS
    OUTPUT_PATH = Path("./data/output")             # Carpeta de salida
    EMBEDDINGS_PATH = Path("./data/embeddings")     # Carpeta con embeddings individuales
    MODEL_NAME = 'multi-qa-MiniLM-L6-cos-v1'        # Modelo de embeddings
    SIMILARITY_THRESHOLD = 0.7
    MIN_SIMILARITY_FILTER = 0.9
    TOP_N_FILTER = 5
    FAISS_TOP_K = 5

# Inicializamos el modelo una sola vez
modelo = SentenceTransformer(Config.MODEL_NAME)

# ============================
# AUXILIARY FUNCTIONS
# ============================
def calcular_hash(file_path: Path) -> str:
    """Calcula el hash MD5 de un archivo (para detectar cambios)."""
    h = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()

def cargar_hash_archivo() -> Dict[str, str]:
    """Carga los hashes guardados de archivos anteriores."""
    if Config.HASH_FILE.exists():
        try:
            with open(Config.HASH_FILE, "rb") as f:
                return pickle.load(f)
        except (pickle.PickleError, FileNotFoundError):
            return {}
    return {}

def guardar_hash(hash_dict: Dict[str, str]) -> None:
    """Guarda los hashes actuales de archivos en un .pkl."""
    Config.HASH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(Config.HASH_FILE, "wb") as f:
        pickle.dump(hash_dict, f)

def hay_archivos_nuevos() -> Tuple[bool, List[str], List[str]]:
    """
    Verifica si hay archivos nuevos, modificados o eliminados en DATA_INPUT.
    Retorna una tupla (hay_cambios, lista_nuevos, lista_eliminados).
    """
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
    """Vacía una carpeta de forma segura (borra archivos y subcarpetas)."""
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
    """Convierte listas o entradas en texto limpio."""
    if isinstance(texto, list):
        return " ".join(map(str, texto))
    return str(texto).strip()

# ============================
# EMBEDDINGS + FAISS
# ============================
def cargar_nuevos_embeddings() -> None:
    """
    Genera embeddings de los PDFs nuevos, los combina en un JSON final
    y crea un índice FAISS para consultas rápidas.
    """
    # Limpiar carpetas de salida
    vaciar_carpeta(Config.OUTPUT_PATH)
    vaciar_carpeta(Config.EMBEDDINGS_PATH)

    # Generar embeddings para cada PDF de entrada
    for archivo in Config.DATA_INPUT.iterdir():
        if archivo.is_file():
            crear_embeddings(str(archivo))

    # Buscar JSONs con embeddings
    data_folder = Config.EMBEDDINGS_PATH
    json_files = list(data_folder.glob("*.json"))
    
    if not json_files:
        print("No JSON files found for processing")
        return

    final_json = Config.EMBE_PATH / "jsonjuntos.json"
    
    if len(json_files) >= 2:
        # Unir el primero y segundo
        juntar_json(str(json_files[0]), str(json_files[1]))
        
        # Seguir uniendo los demás
        for json_file in json_files[2:]:
            juntar_json(str(final_json), str(json_file))
    elif json_files:
        # Si solo hay uno, se copia directamente
        import shutil
        shutil.copy2(str(json_files[0]), str(final_json))

    # Crear índice FAISS con el JSON final
    crear_indices_faiss(str(final_json), str(Config.EMBE_PATH))

def filtrar_por_similitud(pregunta: str, texto: str, modelo_embed: SentenceTransformer, 
                         min_sim: float = Config.MIN_SIMILARITY_FILTER, 
                         top_n: int = Config.TOP_N_FILTER) -> str:
    """
    Filtra partes de un texto que son más similares a la pregunta.
    Retorna solo las partes relevantes.
    """
    if not texto.strip():
        return texto
        
    # Separar texto en frases
    partes = re.split(r'(?<=[.!?])\s+', texto)
    if len(partes) <= 1:
        partes = texto.split(". ")
    
    # Embeddings de pregunta y partes
    emb_q = modelo_embed.encode([pregunta])[0]
    emb_parts = modelo_embed.encode(partes)

    # Calcular similitudes coseno
    sims = []
    for e, p in zip(emb_parts, partes):
        norm_e = np.linalg.norm(e)
        norm_q = np.linalg.norm(emb_q)
        if norm_e > 0 and norm_q > 0:  # Evitar divisiones por 0
            similarity = np.dot(emb_q, e) / (norm_q * norm_e)
            sims.append((similarity, p))

    # Filtrar y ordenar por mayor similitud
    filtered_sims = [s for s in sims if s[0] >= min_sim]
    filtered_sims.sort(key=lambda x: x[0], reverse=True)

    if filtered_sims:
        return " ".join([p for _, p in filtered_sims[:top_n]])
    
    return texto

# ============================
# MAIN QUERY FUNCTION (Para Telegram)
# ============================
def responder_a_consulta(consulta: str) -> str:
    """
    Función principal para responder una consulta (usada en Telegram).
    - Primero intenta con Respuesta_rapida.
    - Si no encuentra nada, devuelve un mensaje de error.
    """
    if Respuesta_rapida(consulta):
        resultado = Respuesta_rapida(consulta)
        """Main function to respond to a query."""   # <- Comentario añadido en tu línea 214
    else:
        resultado = "Por favor, proporciona una consulta válida."
        return resultado
    
    return resultado
