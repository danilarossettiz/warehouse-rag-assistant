"""
scripts/orquestador.py

Conecta el clasificador de intención, RAG, Text-to-SQL y la rama de
definición en una única función responder(), con manejo de estado
de conversación de 1 turno y registro de cada interacción.
"""

import time
from datetime import datetime

from scripts.classify_intent import clasificar
from scripts.retrieval import retrieve
from scripts.generar_respuestas import generar_respuesta_definicion, generar_respuesta_metrica
from scripts.text_to_sql import generar_y_ejecutar
from scripts.rag_utils import formatear_chunks_como_texto
from scripts.interaction_log import registrar_interaccion

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


def _resumir_chunks(chunks: list[dict]) -> list[dict]:
    """Para el log alcanza con el modelo y la distancia, sin el texto."""
    return [
        {"modelo": chunk["modelo"], "distancia": round(chunk["distancia"], 4)}
        for chunk in chunks
    ]


def responder(
    pregunta_usuario: str,
    contexto_anterior: dict | None = None,
    origen: str = "app",
) -> dict:
    """
    Orquesta el flujo completo: clasifica la pregunta y la resuelve con
    el módulo correspondiente (Text-to-SQL para métricas, RAG para
    definiciones, o mensaje fijo si está fuera de alcance).

    Devuelve un dict con la respuesta final y metadata de la ejecución,
    incluyendo el contexto para pasarle al siguiente turno.

    Cada llamada se registra en data/interacciones.jsonl, también
    cuando falla. `origen` distingue el uso real ("app") de las
    corridas de evaluación ("eval") o de prueba.
    """
    inicio = time.perf_counter()
    registro = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "origen": origen,
        "pregunta": pregunta_usuario,
        "pregunta_efectiva": None,
        "categoria": None,
        "confianza": None,
        "chunks": None,
        "sql": None,
        "resultado_texto": None,
        "n_filas": None,
        "respuesta": None,
        "tiempo_seg": None,
        "error": None,
    }

    try:
        pregunta_efectiva = _armar_pregunta_efectiva(pregunta_usuario, contexto_anterior)
        registro["pregunta_efectiva"] = pregunta_efectiva

        categoria, confianza = clasificar(pregunta_efectiva)
        registro["categoria"] = str(categoria)
        registro["confianza"] = float(confianza)

        resultado_metadata = {
            "categoria": categoria,
            "confianza": confianza,
            "sql": None,
            "chunks_recuperados": None,
            "datos": None,
        }

        if categoria == "metrica":
            chunks = retrieve(pregunta_efectiva)
            registro["chunks"] = _resumir_chunks(chunks)

            contexto_rag = formatear_chunks_como_texto(chunks)
            sql, resultado, datos = generar_y_ejecutar(pregunta_efectiva, contexto_rag)
            registro["sql"] = sql
            registro["resultado_texto"] = resultado
            registro["n_filas"] = len(datos[1]) if datos else None

            respuesta = generar_respuesta_metrica(pregunta_efectiva, resultado)
            resultado_metadata["sql"] = sql
            resultado_metadata["chunks_recuperados"] = chunks
            resultado_metadata["datos"] = datos

        elif categoria == "definicion":
            chunks = retrieve(pregunta_efectiva)
            registro["chunks"] = _resumir_chunks(chunks)

            respuesta = generar_respuesta_definicion(pregunta_efectiva, chunks)
            resultado_metadata["chunks_recuperados"] = chunks

        else:  # "fuera_de_alcance"
            respuesta = MENSAJE_FUERA_DE_ALCANCE

        registro["respuesta"] = respuesta

        contexto_nuevo = {
            "pregunta": pregunta_usuario,
            "categoria": categoria,
        }

        return {
            "respuesta": respuesta,
            "contexto_anterior": contexto_nuevo,
            **resultado_metadata,
        }

    except Exception as error:
        registro["error"] = {"tipo": type(error).__name__, "mensaje": str(error)}
        raise  # el error sigue su camino: app.py ya lo captura y lo muestra

    finally:
        registro["tiempo_seg"] = round(time.perf_counter() - inicio, 3)
        registrar_interaccion(registro)