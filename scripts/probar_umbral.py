"""
scripts/probar_umbral.py

Corre retrieve() sobre preguntas dentro y fuera de alcance
para calibrar el umbral de distancia coseno de rechazo.
"""

from scripts.retrieval import retrieve

PREGUNTAS_DENTRO_DE_ALCANCE = [
    "¿qué significa la columna delivery_days?",
    "¿cómo se calcula el revenue mensual?",
    "¿qué es orders_rank en la tabla de categorías?",
    "¿qué representa la tabla int_orders__enriched?",
]

PREGUNTAS_FUERA_DE_ALCANCE = [
    "¿cuál es la capital de Francia?",
    "¿qué opinás del Mundial de fútbol?",
    "contame una receta de pastel de papas",
    "¿quién ganó las elecciones en Argentina?",
]


def probar(preguntas: list[str], etiqueta: str) -> None:
    print(f"\n--- {etiqueta} ---")
    for pregunta in preguntas:
        chunks = retrieve(pregunta, k=3)
        distancia_top = chunks[0]["distancia"] if chunks else None
        print(f"{distancia_top:.4f}  |  {pregunta}")


if __name__ == "__main__":
    probar(PREGUNTAS_DENTRO_DE_ALCANCE, "DENTRO DE ALCANCE")
    probar(PREGUNTAS_FUERA_DE_ALCANCE, "FUERA DE ALCANCE")
