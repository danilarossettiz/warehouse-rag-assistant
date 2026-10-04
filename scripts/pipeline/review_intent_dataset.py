"""
Revision rapida por terminal del CSV de candidatos del clasificador de
intencion. Muestra una pregunta por vez y con una sola tecla se decide
que hacer con ella. El progreso se guarda despues de cada decision.

Teclas:
  y -> aceptar la etiqueta sugerida
  m -> corregir etiqueta a "metrica"
  d -> corregir etiqueta a "definicion"
  f -> corregir etiqueta a "fuera_de_alcance"
  x -> descartar esta pregunta (se borra)
  n -> dejar pendiente/dudosa (no se marca como revisada, se vuelve a mostrar en otra pasada)
  q -> guardar y salir (podes continuar despues donde quedaste)
"""

import csv
import sys
import termios
import tty
from pathlib import Path

CSV_PATH = Path("data/intent_dataset_candidates.csv")

LABELS = {
    "m": "metrica",
    "d": "definicion",
    "f": "fuera_de_alcance",
}

TECLAS_VALIDAS = {"y", "m", "d", "f", "x", "n", "q"}


def getch() -> str:
    """Lee un solo caracter del teclado, sin esperar Enter."""
    fd = sys.stdin.fileno()
    estado_previo = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, estado_previo)
    return ch


def guardar(filas: list[dict]) -> None:
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["question", "label", "reviewed"])
        writer.writeheader()
        writer.writerows(filas)


def main():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    pendientes = [i for i, fila in enumerate(filas) if fila["reviewed"] != "si"]
    total_pendientes = len(pendientes)

    if total_pendientes == 0:
        print("No hay preguntas pendientes de revision. Todo revisado.")
        return

    print(f"Preguntas pendientes: {total_pendientes}")
    print("y=aceptar | m/d/f=corregir etiqueta | x=descartar | n=dejar pendiente | q=guardar y salir\n")

    a_borrar = []

    for n_idx, i in enumerate(pendientes, start=1):
        fila = filas[i]
        print(f"[{n_idx}/{total_pendientes}] etiqueta sugerida: {fila['label']}")
        print(f"  {fila['question']}")

        while True:
            tecla = getch().lower()
            if tecla in TECLAS_VALIDAS:
                break
            print("  (tecla no reconocida, proba con y/m/d/f/x/n/q)")

        print()

        if tecla == "q":
            print("Guardando progreso y saliendo...")
            break
        elif tecla == "x":
            a_borrar.append(i)
        elif tecla == "n":
            pass
        elif tecla in LABELS:
            fila["label"] = LABELS[tecla]
            fila["reviewed"] = "si"
        elif tecla == "y":
            fila["reviewed"] = "si"

    filas_finales = [fila for idx, fila in enumerate(filas) if idx not in a_borrar]
    guardar(filas_finales)

    revisadas = sum(1 for fila in filas_finales if fila["reviewed"] == "si")
    print(f"\nGuardado. {revisadas}/{len(filas_finales)} filas revisadas en total.")
    print("Resumen por categoria (solo revisadas):")
    for etiqueta in ("metrica", "definicion", "fuera_de_alcance"):
        cantidad = sum(
            1 for fila in filas_finales
            if fila["reviewed"] == "si" and fila["label"] == etiqueta
        )
        print(f"  {etiqueta}: {cantidad}")


if __name__ == "__main__":
    main()
