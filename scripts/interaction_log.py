"""
scripts/interaction_log.py

Registro de interacciones del asistente en formato JSONL (JSON Lines):
una línea JSON por interacción, para analizarlas después con pandas.
"""

import json
import sys
from pathlib import Path

RUTA_LOG = Path("data/interacciones.jsonl")


def registrar_interaccion(registro: dict) -> None:
    """
    Agrega un registro como una línea al final de RUTA_LOG.

    Nunca lanza excepciones: el log es secundario, y una falla al
    escribirlo (disco lleno, permisos) no debe romper la respuesta
    al usuario. En ese caso solo se avisa por stderr.
    """
    try:
        RUTA_LOG.parent.mkdir(parents=True, exist_ok=True)

        # ensure_ascii=False conserva las tildes; default=str convierte a
        # texto lo que JSON no entiende (Decimal, date, np.str_, etc.)
        linea = json.dumps(registro, ensure_ascii=False, default=str)

        with open(RUTA_LOG, "a", encoding="utf-8") as archivo:
            archivo.write(linea + "\n")
    except Exception as error:
        print(
            f"Advertencia: no se pudo escribir el log "
            f"({type(error).__name__}: {error})",
            file=sys.stderr,
        )
