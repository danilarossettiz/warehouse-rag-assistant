"""
Prueba rápida: le hacemos una pregunta en español a la colección
y vemos qué chunks de documentación (en inglés) devuelve como más parecidos.
"""

import chromadb
from sentence_transformers import SentenceTransformer

PERSIST_DIR = "chroma_db"
COLLECTION_NAME = "dbt_docs"
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def main():
    print(f"Cargando modelo '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Conectando a Chroma en ./{PERSIST_DIR}...")
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    collection = client.get_collection(name=COLLECTION_NAME)

    # Cambiá esta pregunta por cualquier otra que quieras probar
    query = "¿qué es un pedido enriquecido?"

    print(f"\nPregunta: {query}")
    query_embedding = model.encode([query])[0].tolist()

    # n_results=3 le pide a Chroma los 3 chunks más parecidos
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    print("\nResultados más parecidos:\n")
    for i, (doc, metadata, distance) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    )):
        print(f"--- Resultado {i+1} (distancia: {distance:.4f}) ---")
        print(f"Modelo: {metadata['model']}")
        print(f"Texto: {doc[:200]}...")
        print()


if __name__ == "__main__":
    main()
