"""
Filtra las filas aprobadas (reviewed == "si") del CSV de candidatos y
genera el dataset final del clasificador de intencion, sin la columna
reviewed (ya no aporta nada una vez aprobado todo).
"""

import csv
from pathlib import Path

INPUT_PATH = Path("data/intent_dataset_candidates.csv")
OUTPUT_PATH = Path("data/intent_dataset.csv")


def main():
    with open(INPUT_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    aprobadas = [fila for fila in filas if fila["reviewed"] == "si"]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "label"])
        writer.writeheader()
        for fila in aprobadas:
            writer.writerow({"question": fila["question"], "label": fila["label"]})

    print(f"Dataset final: {len(aprobadas)} preguntas en {OUTPUT_PATH}")
    conteo = {}
    for fila in aprobadas:
        conteo[fila["label"]] = conteo.get(fila["label"], 0) + 1
    for etiqueta, cantidad in conteo.items():
        print(f"  {etiqueta}: {cantidad}")


if __name__ == "__main__":
    main()
