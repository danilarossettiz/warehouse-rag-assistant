"""
Corre retrieve() sobre preguntas ancla de definición (mismas de
scripts/eval/evaluar_sistema.py, copiadas aquí para no importar ese
módulo: arrastra scripts.orquestador y, con él, scripts.gemini_client,
que lee GEMINI_API_KEY al importarse) y verifica que el chunk esperado
esté entre los recuperados.

Requiere el índice de Chroma ya construido en chroma_db/ (no se versiona
en git). Si no existe, los tests se saltan con un mensaje explicando
cómo generarlo.
"""

import pytest
from chromadb.errors import NotFoundError

from scripts.retrieval import retrieve

CASOS = [
    (
        'Qué significa el estado de pedido "shipped" en nuestro modelo de datos?',
        "stg_olist__orders",
    ),
    (
        '¿Cómo se calcula el "review_score" de un pedido?',
        "stg_olist__order_reviews",
    ),
]


@pytest.fixture(scope="module", autouse=True)
def _requiere_indice_chroma():
    try:
        retrieve("ping", k=1)
    except NotFoundError:
        pytest.skip(
            "No se encontró el índice de Chroma en chroma_db/. Generalo con "
            "'python3 -m scripts.pipeline.build_vector_store' antes de correr "
            "estos tests (usa data/dbt_docs_embeddings.json, que sí está en el repo)."
        )


@pytest.mark.parametrize("pregunta, modelo_esperado", CASOS)
def test_recupera_modelo_esperado(pregunta, modelo_esperado):
    resultados = retrieve(pregunta, k=5)
    modelos = [r["modelo"] for r in resultados]
    assert modelo_esperado in modelos


@pytest.mark.xfail(
    reason=(
        "El prefijo de contexto que antepone orquestador._armar_pregunta_efectiva "
        "('(Pregunta anterior: ...)') degrada el retrieval de preguntas cortas de "
        "seguimiento: int_orders__enriched deja de aparecer en el top-5."
    ),
    strict=True,
)
def test_recupera_modelo_esperado_con_prefijo_de_contexto():
    pregunta_con_contexto = (
        "(Pregunta anterior: ¿Cuál fue el ingreso total por mes en 2018?) "
        "¿qué significa la columna delivery_days?"
    )
    resultados = retrieve(pregunta_con_contexto, k=5)
    modelos = [r["modelo"] for r in resultados]
    assert "int_orders__enriched" in modelos
