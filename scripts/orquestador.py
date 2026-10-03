"""
scripts/orquestador.py

Conecta el clasificador de intención, RAG, Text-to-SQL y la rama de
definición en una única función responder(), con manejo de estado
de conversación de 1 turno.
"""

from scripts.classify_intent import clasificar
from scripts.retrieval import retrieve
from scripts.generar_respuestas import generar_respuesta_definicion, generar_respuesta_metrica
from scripts.text_to_sql import generar_y_ejecutar
from scripts.rag_utils import formatear_chunks_como_texto

MENSAJE_FUERA_DE_ALCANCE = (
    "No puedo responder eso. Puedo ayudarte con preguntas sobre las "
    "tablas y columnas del warehouse de Olist, o con métricas de negocio "
    "como facturación, categorías de producto y tiempos de entrega."
)


def _armar_pregunta_efectiva(pregunta_usuario: str, contexto_anterior: dict | None) -> str:
    """
    Si hay contexto de un turno anterior, lo antepone a la pregunta actual
    para dar continuidad a preguntas de seguimiento (ej. "¿y en agosto?").
    """
    if not contexto_anterior:
        return pregunta_usuario

    return (
        f"(Pregunta anterior: {contexto_anterior['pregunta']}) "
        f"{pregunta_usuario}"
    )


def responder(pregunta_usuario: str, contexto_anterior: dict | None = None) -> dict:
    """
    Orquesta el flujo completo: clasifica la pregunta y la resuelve con
    el módulo correspondiente (Text-to-SQL para métricas, RAG para
    definiciones, o mensaje fijo si está fuera de alcance).

    Devuelve un dict con la respuesta final y metadata de la ejecución,
    incluyendo el contexto para pasarle al siguiente turno.
    """
    pregunta_efectiva = _armar_pregunta_efectiva(pregunta_usuario, contexto_anterior)

    categoria, confianza = clasificar(pregunta_efectiva)

    resultado_metadata = {
        "categoria": categoria,
        "confianza": confianza,
        "sql": None,
        "chunks_recuperados": None,
        "datos": None,
    }

    if categoria == "metrica":
        chunks = retrieve(pregunta_efectiva)
        contexto_rag = formatear_chunks_como_texto(chunks)
        sql, resultado, datos = generar_y_ejecutar(pregunta_efectiva, contexto_rag)

        respuesta = generar_respuesta_metrica(pregunta_efectiva, resultado)
        resultado_metadata["sql"] = sql
        resultado_metadata["chunks_recuperados"] = chunks
        resultado_metadata["datos"] = datos

    elif categoria == "definicion":
        chunks = retrieve(pregunta_efectiva)
        respuesta = generar_respuesta_definicion(pregunta_efectiva, chunks)

        resultado_metadata["chunks_recuperados"] = chunks

    else:  # "fuera_de_alcance"
        respuesta = MENSAJE_FUERA_DE_ALCANCE

    contexto_nuevo = {
        "pregunta": pregunta_usuario,
        "categoria": categoria,
    }

    return {
        "respuesta": respuesta,
        "contexto_anterior": contexto_nuevo,
        **resultado_metadata,
    }
