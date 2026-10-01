"""
scripts/probar_generalizacion_e2e.py

Evalúa las 7 preguntas de generalización a través del orquestador
completo (responder()), en vez de llamar a generar_y_ejecutar()
directamente con contexto perfecto a mano. Esto prueba el pipeline
real: clasificador -> retrieve() -> módulo correspondiente.
"""

from scripts.orquestador import responder

PREGUNTAS = [
    "¿Cuál fue el ingreso total en marzo de 2018?",
    "¿Cuál fue el ingreso promedio por pedido en 2018?",
    "¿Cuáles son las 10 categorías más vendidas por cantidad de pedidos?",
    "¿Cuál es la categoría con más ingresos?",
    "¿Cuántos pedidos se hicieron en cada categoría del top 3?",
    "¿Cuál es el estado con mayor tiempo de entrega?",
    "¿Cuál es el estado con menor tiempo de entrega promedio?",
]

if __name__ == "__main__":
    exitosas = 0
    clasificadas_como_metrica = 0

    for i, pregunta in enumerate(PREGUNTAS, start=1):
        print(f"\n{'=' * 60}")
        print(f"Pregunta {i}: {pregunta}")
        print("=" * 60)

        resultado = responder(pregunta)

        print(f"Categoría: {resultado['categoria']} (confianza: {resultado['confianza']:.4f})")
        print(f"Respuesta: {resultado['respuesta']}")

        if resultado["categoria"] == "metrica":
            clasificadas_como_metrica += 1
            if resultado["sql"] and "No pude generar" not in str(resultado["respuesta"]):
                exitosas += 1
        else:
            print(f"⚠️  ESPERABA 'metrica', CLASIFICÓ COMO '{resultado['categoria']}'")

    print(f"\n\n{'#' * 60}")
    print(f"Clasificadas correctamente como 'metrica': {clasificadas_como_metrica}/{len(PREGUNTAS)}")
    print(f"Resueltas exitosamente end-to-end: {exitosas}/{len(PREGUNTAS)}")
    print("#" * 60)
