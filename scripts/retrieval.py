"""
Módulo de retrieval reutilizable.

Expone retrieve(pregunta, k) para que el resto del sistema
(clasificador, integración, evaluación) pueda pedir los chunks
de documentación más relevantes para una pregunta dada.
"""

import chromadb
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "dbt_docs"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Variables "privadas" del módulo, para no recargar el modelo
# ni reconectar a Chroma en cada llamada a retrieve().
_model = None
_collection = None


def _get_model():
    """Carga el modelo de embeddings una sola vez y lo reutiliza."""
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    """Conecta a la colección de Chroma una sola vez y la reutiliza."""
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=PERSIST_DIR)
        _collection = client.get_collection(name=COLLECTION_NAME)
    return _collection


def retrieve(pregunta: str, k: int = 3) -> list[dict]:
    """
    Busca los k chunks de documentación más relevantes para una pregunta.

    Args:
        pregunta: la pregunta del usuario, en español.
        k: cantidad de chunks a devolver.

    Returns:
        Lista de diccionarios, ordenados del más al menos relevante:
        [{"modelo": str, "texto": str, "distancia": float}, ...]
    """
    model = _get_model()
    collection = _get_collection()

    query_embedding = model.encode([pregunta])[0].tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k
    )

    chunks = []
    for doc, metadata, distance in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        chunks.append({
            "modelo": metadata["model"],
            "texto": doc,
            "distancia": distance
        })
    return chunks


if __name__ == "__main__":
    # Prueba manual rápida: python scripts/retrieval.py
    pregunta = "¿qué es un pedido enriquecido?"
    resultados = retrieve(pregunta, k=3)
    print(f"Pregunta: {pregunta}\n")
    for i, r in enumerate(resultados):
        print(f"--- Resultado {i+1} (distancia: {r['distancia']:.4f}) ---")
        print(f"Modelo: {r['modelo']}")
        print(f"Texto: {r['texto'][:200]}...\n")
