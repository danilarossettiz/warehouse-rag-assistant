"""
Clasifica las preguntas ancla del proyecto (mismas de
scripts/eval/evaluar_sistema.py, copiadas aquí para no importar ese
módulo: arrastra scripts.orquestador y, con él, scripts.gemini_client,
que lee GEMINI_API_KEY al importarse) y verifica que el clasificador
de intención les asigne la categoría esperada.
"""

import pytest

from scripts.classify_intent import clasificar

CASOS = [
    ("¿Cuál fue el ingreso total por mes en 2018?", "metrica"),
    (
        "¿Cuáles son las 5 categorías de productos más vendidas por cantidad de pedidos?",
        "metrica",
    ),
    ("¿Cuál es el tiempo promedio de entrega por estado de Brasil?", "metrica"),
    (
        'Qué significa el estado de pedido "shipped" en nuestro modelo de datos?',
        "definicion",
    ),
    ('¿Cómo se calcula el "review_score" de un pedido?', "definicion"),
    ("¿Cuál va a ser el clima mañana en San Pablo?", "fuera_de_alcance"),
    (
        "¿Podés recomendarme qué producto comprar para un regalo de cumpleaños?",
        "fuera_de_alcance",
    ),
    pytest.param(
        "¿Qué indica orders_rank en el desempeño por categoría?",
        "definicion",
        marks=pytest.mark.xfail(
            reason=(
                "Defecto conocido (docs/evaluacion_resultados.csv, caso D3): "
                "el clasificador confunde esta definición con una métrica."
            ),
            strict=True,
        ),
    ),
]


@pytest.mark.parametrize("pregunta, categoria_esperada", CASOS)
def test_clasifica_pregunta_ancla(pregunta, categoria_esperada):
    categoria, _confianza = clasificar(pregunta)
    assert categoria == categoria_esperada
