"""
Genera embeddings para cada chunk de documentación dbt.
Usa un modelo multilingüe local (sentence-transformers) para que
preguntas en español puedan encontrar documentación en inglés.
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Rutas de entrada y salida
INPUT_PATH = Path("data/dbt_docs_chunks.json")
OUTPUT_PATH = Path("data/dbt_docs_embeddings.json")

# Nombre del modelo en Hugging Face. La primera vez que corras esto,
# se descarga automáticamente (~470MB) y se cachea en tu disco
# (por default en ~/.cache/torch/sentence_transformers).
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def main():
    print(f"Cargando modelo '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    print(f"Leyendo chunks desde {INPUT_PATH}...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Generando embeddings para {len(chunks)} chunks...")
    # Extraemos solo el texto de cada chunk para pasárselo al modelo
    texts = [chunk["chunk_text"] for chunk in chunks]

    # encode() convierte cada texto en un vector de 384 números.
    # show_progress_bar=True te muestra el avance en la terminal.
    embeddings = model.encode(texts, show_progress_bar=True)

    # Combinamos cada chunk original con su embedding correspondiente.
    # .tolist() convierte el array de numpy en una lista de Python,
    # que sí se puede guardar directamente como JSON.
    output = []
    for chunk, embedding in zip(chunks, embeddings):
        output.append({
            **chunk,
            "embedding": embedding.tolist()
        })

    print(f"Guardando resultado en {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Listo.")


if __name__ == "__main__":
    main()