"""
Validación del checklist de Etapa 3: probar retrieve() con las
preguntas ancla de definición (RAG) del set de validación del proyecto,
y revisar manualmente si el contexto recuperado tiene sentido.
"""

from retrieval import retrieve

# Las 2 preguntas de definición de docs/preguntas_ancla.md
PREGUNTAS_DEFINICION = [
    '¿Qué significa el estado de pedido "shipped" en nuestro modelo de datos?',
    '¿Cómo se calcula el "review_score" de un pedido?',
]


def main():
    for pregunta in PREGUNTAS_DEFINICION:
        print("=" * 80)
        print(f"Pregunta: {pregunta}\n")

        resultados = retrieve(pregunta, k=3)

        for i, r in enumerate(resultados):
            print(f"--- Resultado {i+1} (distancia: {r['distancia']:.4f}) ---")
            print(f"Modelo: {r['modelo']}")
            print(f"Texto: {r['texto'][:300]}...\n")

    print("=" * 80)


if __name__ == "__main__":
    main()
