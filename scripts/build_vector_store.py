"""
Carga los embeddings ya generados en una base vectorial Chroma,
persistida en disco para no tener que regenerarla cada vez.
"""

import json
from pathlib import Path
import chromadb

INPUT_PATH = Path("data/dbt_docs_embeddings.json")

# Carpeta donde Chroma va a guardar el índice en disco.
# Si la carpeta ya existe con datos, Chroma los reutiliza en vez de perderlos.
PERSIST_DIR = "chroma_db"

COLLECTION_NAME = "dbt_docs"


def main():
    print(f"Leyendo embeddings desde {INPUT_PATH}...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # PersistentClient guarda todo en la carpeta PERSIST_DIR en vez de
    # mantenerlo solo en memoria. Es lo que te permite cerrar el script
    # y, la próxima vez, cargar el índice ya armado sin recalcular nada.
    print(f"Conectando a Chroma (persistiendo en ./{PERSIST_DIR})...")
    client = chromadb.PersistentClient(path=PERSIST_DIR)

    # Si la colección ya existe de una corrida anterior, la borramos
    # para no duplicar documentos si volvés a correr este script.
    existing = [c.name for c in client.list_collections()]
    if COLLECTION_NAME in existing:
        print(f"La colección '{COLLECTION_NAME}' ya existe, la borro para recrearla...")
        client.delete_collection(COLLECTION_NAME)

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    # Preparamos las cuatro listas paralelas que pide Chroma:
    # ids, documentos (texto), embeddings y metadata.
    ids = []
    documents = []
    embeddings = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"chunk_{i}_{chunk['model']}")
        documents.append(chunk["chunk_text"])
        embeddings.append(chunk["embedding"])
        metadatas.append({
            "model": chunk["model"],
            # Guardamos el resto de la metadata original como JSON string,
            # porque Chroma no acepta diccionarios anidados como valor.
            "metadata_json": json.dumps(chunk["metadata"], ensure_ascii=False)
        })

    print(f"Insertando {len(ids)} chunks en la colección...")
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(f"Listo. Colección '{COLLECTION_NAME}' persistida en ./{PERSIST_DIR}")
    print(f"Total de documentos en la colección: {collection.count()}")


if __name__ == "__main__":
    main()