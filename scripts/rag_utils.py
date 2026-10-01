"""
scripts/rag_utils.py

Utilidades compartidas para trabajar con los chunks recuperados por RAG.
"""


def formatear_chunks_como_texto(chunks: list[dict]) -> str:
    """
    Convierte una lista de chunks recuperados por retrieve() en un solo
    string de contexto, listo para inyectar en un prompt.
    """
    return "\n\n".join(
        f"[Modelo: {chunk['modelo']}]\n{chunk['texto']}"
        for chunk in chunks
    )
