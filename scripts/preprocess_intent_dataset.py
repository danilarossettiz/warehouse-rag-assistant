"""
Preprocesamiento del dataset del clasificador de intencion:
- limpieza basica de texto (minusculas, sin acentos)
- split train/test 80/20 manteniendo el balance de clases

La tokenizacion "real" (cortar en palabras para el modelo) la hace
scikit-learn automaticamente en el paso de vectorizacion (TF-IDF), que
es el siguiente punto del checklist. Aca solo dejamos el texto limpio
y consistente, y calculamos un diagnostico de cantidad de palabras.
"""

import csv
import unicodedata
from pathlib import Path

from sklearn.model_selection import train_test_split

INPUT_PATH = Path("data/intent_dataset.csv")
TRAIN_PATH = Path("data/intent_train.csv")
TEST_PATH = Path("data/intent_test.csv")

TEST_SIZE = 0.2
RANDOM_STATE = 42


def limpiar_texto(texto: str) -> str:
    """Minusculas + sin acentos + espacios simples."""
    texto = texto.lower().strip()
    # Descompone letras con acento en letra + marca de acento, y descarta la marca
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = " ".join(texto.split())  # colapsa espacios multiples
    return texto


def main():
    with open(INPUT_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    for fila in filas:
        fila["question_clean"] = limpiar_texto(fila["question"])

    # Diagnostico de tokenizacion: cantidad de palabras por pregunta
    largos = [len(fila["question_clean"].split()) for fila in filas]
    print(f"Preguntas totales: {len(filas)}")
    print(f"Palabras por pregunta: min={min(largos)}, max={max(largos)}, "
          f"promedio={sum(largos)/len(largos):.1f}")

    labels = [fila["label"] for fila in filas]
    train, test = train_test_split(
        filas,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    fieldnames = ["question", "question_clean", "label"]

    for path, subset in ((TRAIN_PATH, train), (TEST_PATH, test)):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for fila in subset:
                writer.writerow({k: fila[k] for k in fieldnames})

    print(f"\nTrain: {len(train)} preguntas -> {TRAIN_PATH}")
    print(f"Test:  {len(test)} preguntas -> {TEST_PATH}")

    for nombre, subset in (("Train", train), ("Test", test)):
        print(f"\nBalance en {nombre}:")
        for etiqueta in ("metrica", "definicion", "fuera_de_alcance"):
            cantidad = sum(1 for fila in subset if fila["label"] == etiqueta)
            print(f"  {etiqueta}: {cantidad}")


if __name__ == "__main__":
    main()
