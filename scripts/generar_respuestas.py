"""
scripts/generar_respuestas.py

Genera respuestas en lenguaje natural para preguntas definicionales,
usando RAG (retrieval.py) como fuente de contexto y Gemini para
redactar la respuesta final.
"""

from scripts.gemini_client import llamar_gemini
from scripts.rag_utils import formatear_chunks_como_texto

UMBRAL_DISTANCIA = 0.65

MENSAJE_FUERA_DE_ALCANCE = (
    "No tengo información sobre eso en la documentación del proyecto. "
    "Puedo responder preguntas sobre las tablas y columnas del warehouse "
    "de Olist (ventas, pedidos, productos, entregas, etc.)."
)


def _armar_prompt_definicion(pregunta: str, chunks: list[dict]) -> str:
    """
    Arma el prompt para Gemini combinando la pregunta del usuario
    con el texto de los chunks recuperados por RAG.
    """
    contexto = formatear_chunks_como_texto(chunks)

    prompt = f"""Sos un asistente que responde preguntas sobre un data warehouse de e-commerce (dataset Olist).

Respondé la siguiente pregunta ÚNICAMENTE usando la información del contexto de abajo.
No uses conocimiento general de e-commerce ni inventes detalles que no estén en el contexto.
Si el contexto no contiene información suficiente para responder, decilo explícitamente.
Respondé en español, de forma clara y concisa (2-4 oraciones).

Contexto:
{contexto}

Pregunta: {pregunta}

Respuesta:"""

    return prompt


def generar_respuesta_definicion(pregunta: str, chunks: list[dict]) -> str:
    """
    Genera una respuesta en lenguaje natural para una pregunta definicional.

    - Si no hay chunks, o el chunk más relevante supera el umbral de
      distancia coseno, se devuelve el mensaje fijo de fuera de alcance
      (sin llamar a Gemini).
    - Si el contexto es relevante, se arma un prompt con los chunks y
      se llama a Gemini para redactar la respuesta.
    """
    if not chunks or chunks[0]["distancia"] > UMBRAL_DISTANCIA:
        return MENSAJE_FUERA_DE_ALCANCE

    prompt = _armar_prompt_definicion(pregunta, chunks)
    respuesta = llamar_gemini(prompt)
    return respuesta


def _armar_prompt_metrica(pregunta: str, resultado: str) -> str:
    """
    Arma el prompt para que Gemini redacte (no calcule) una respuesta
    a partir del resultado de la query ya ejecutada.
    """
    return f"""Sos un asistente que explica resultados de un data warehouse de e-commerce (dataset Olist).

Redactá una respuesta breve (1 a 3 oraciones, en español) a la pregunta, usando ÚNICAMENTE los datos del resultado de abajo.

Reglas:
- Citá los números exactamente como aparecen. No los redondees ni los recalcules, y no calcules totales ni promedios nuevos.
- No expliques causas ni agregues interpretaciones que los datos no muestren.
- Si el resultado tiene muchas filas, resumí lo más relevante (por ejemplo el máximo, el mínimo o la tendencia general) en vez de listarlas todas.
- Si el resultado está vacío, decí que la consulta no devolvió datos.

Pregunta: {pregunta}

Resultado de la consulta:
{resultado}

Respuesta:"""


def generar_respuesta_metrica(pregunta: str, resultado: str) -> str:
    """
    Redacta en lenguaje natural el resultado de una consulta de métricas.

    Si Gemini falla (timeout, límite de requests, error de red), no se
    corta el flujo: se devuelve un aviso con el tipo de error y el
    resultado crudo, para que el usuario igual vea los datos.
    """
    prompt = _armar_prompt_metrica(pregunta, resultado)

    try:
        return llamar_gemini(prompt).strip()
    except Exception as error:
        return (
            f"No pude redactar la explicación ({type(error).__name__}: {error}). "
            f"Este es el resultado crudo:\n{resultado}"
        )