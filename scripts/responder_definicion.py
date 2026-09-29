"""
scripts/responder_definicion.py

Genera respuestas en lenguaje natural para preguntas definicionales,
usando RAG (retrieval.py) como fuente de contexto y Gemini para
redactar la respuesta final.
"""

from scripts.gemini_client import llamar_gemini

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
    contexto = "\n\n".join(
        f"[Modelo: {chunk['modelo']}]\n{chunk['texto']}"
        for chunk in chunks
    )

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
