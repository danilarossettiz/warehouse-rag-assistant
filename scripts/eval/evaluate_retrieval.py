"""
Evaluación mínima del RAG (Etapa 3, último ítem del checklist).

Corre retrieve() sobre las 7 preguntas ancla del proyecto y genera
un archivo markdown en docs/ con los resultados, para que la anotación
manual (¿el contexto recuperado es correcto? sí/no) se haga directamente
sobre ese documento.
"""

from retrieval import retrieve

# Las 7 preguntas ancla de docs/preguntas_ancla.md, con su tipo.
PREGUNTAS_ANCLA = [
    {"tipo": "Métrica", "pregunta": "¿Cuál fue el ingreso total por mes en 2018?"},
    {"tipo": "Métrica", "pregunta": "¿Cuáles son las 5 categorías de productos más vendidas por cantidad de pedidos?"},
    {"tipo": "Métrica", "pregunta": "¿Cuál es el tiempo promedio de entrega por estado de Brasil?"},
    {"tipo": "Definición", "pregunta": '¿Qué significa el estado de pedido "shipped" en nuestro modelo de datos?'},
    {"tipo": "Definición", "pregunta": '¿Cómo se calcula el "review_score" de un pedido?'},
    {"tipo": "Fuera de alcance", "pregunta": "¿Cuál va a ser el clima mañana en San Pablo?"},
    {"tipo": "Fuera de alcance", "pregunta": "¿Podés recomendarme qué producto comprar para un regalo de cumpleaños?"},
]

OUTPUT_PATH = "docs/retrieval_evaluation.md"


def main():
    lineas = [
        "# Evaluación mínima de retrieval (Etapa 3)",
        "",
        "Resultados de `retrieve(pregunta, k=3)` sobre las 7 preguntas ancla.",
        "",
        "Para las preguntas de **Definición**, anotar sí/no según si el chunk",
        "con la respuesta real aparece dentro del top-3.",
        "",
        "Para **Métrica** y **Fuera de alcance**, no hay chunk 'correcto' —",
        "anotar si la distancia es notablemente más alta que en las de",
        "Definición (señal útil para el umbral de rechazo del clasificador).",
        "",
    ]

    for item in PREGUNTAS_ANCLA:
        tipo = item["tipo"]
        pregunta = item["pregunta"]
        resultados = retrieve(pregunta, k=3)

        lineas.append(f"## [{tipo}] {pregunta}")
        lineas.append("")
        lineas.append("**¿Correcto? (completar a mano):** [ ] Sí   [ ] No")
        lineas.append("")

        for i, r in enumerate(resultados):
            lineas.append(f"- **Resultado {i + 1}** (modelo: `{r['modelo']}`, distancia: {r['distancia']:.4f})")
            lineas.append("  ```")
            lineas.append(f"  {r['texto'][:300].strip()}...")
            lineas.append("  ```")

        lineas.append("")
        lineas.append("---")
        lineas.append("")

    contenido = "\n".join(lineas)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(contenido)

    print(f"Evaluación generada en: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
