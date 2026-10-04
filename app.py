"""
app.py

Interfaz de chat en Streamlit para el asistente del warehouse Olist.
Toda la lógica vive en scripts/orquestador.py: este archivo solo
presenta lo que devuelve responder().
"""

import uuid

import pandas as pd
import streamlit as st

from scripts.orquestador import responder

TITULO_POR_DEFECTO = "Nueva conversación"

st.set_page_config(page_title="Asistente del warehouse Olist", page_icon="📦")
st.title("Asistente del warehouse Olist")
st.caption(
    "Preguntá por métricas de negocio (ingresos, categorías, entregas) "
    "o por la definición de tablas y columnas del warehouse."
)

# --- Estado que persiste entre ejecuciones del script ---
if "conversaciones" not in st.session_state:
    st.session_state.conversaciones = {}
if "conversacion_activa" not in st.session_state:
    st.session_state.conversacion_activa = None


def crear_conversacion() -> None:
    """Crea una conversación vacía y la deja como activa."""
    id_nueva = uuid.uuid4().hex[:8]
    st.session_state.conversaciones[id_nueva] = {
        "titulo": TITULO_POR_DEFECTO,
        "mensajes": [],
        "contexto_anterior": None,
    }
    st.session_state.conversacion_activa = id_nueva


def mostrar_mensaje(mensaje: dict) -> None:
    """Dibuja un mensaje completo: texto, y si los tiene, SQL y tabla."""
    with st.chat_message(mensaje["rol"]):
        st.write(mensaje["texto"])

        if mensaje.get("sql"):
            with st.expander("Ver SQL generado"):
                st.code(mensaje["sql"], language="sql")

        if mensaje.get("datos"):
            columnas, filas = mensaje["datos"]
            if filas:
                st.dataframe(
                    pd.DataFrame(filas, columns=columnas),
                    hide_index=True,
                )


# Siempre tiene que haber una conversación activa
if st.session_state.conversacion_activa is None:
    crear_conversacion()

conversacion = st.session_state.conversaciones[st.session_state.conversacion_activa]

# --- Redibujar el historial (el script corre de cero en cada interacción) ---
for mensaje in conversacion["mensajes"]:
    mostrar_mensaje(mensaje)

# --- Entrada del usuario ---
pregunta = st.chat_input("Preguntá sobre los datos de Olist...")

if pregunta and pregunta.strip():
    # La primera pregunta le pone título a la conversación
    if not conversacion["mensajes"]:
        recorte = pregunta[:40]
        conversacion["titulo"] = recorte + ("…" if len(pregunta) > 40 else "")

    mensaje_usuario = {"rol": "user", "texto": pregunta}
    conversacion["mensajes"].append(mensaje_usuario)
    mostrar_mensaje(mensaje_usuario)

    with st.spinner("Pensando..."):
        try:
            r = responder(pregunta, conversacion["contexto_anterior"])
            mensaje_asistente = {
                "rol": "assistant",
                "texto": r["respuesta"],
                "sql": r["sql"],
                "datos": r["datos"],
                "categoria": str(r["categoria"]),
                "confianza": float(r["confianza"]),
                "chunks": r["chunks_recuperados"],
            }
            conversacion["contexto_anterior"] = r["contexto_anterior"]
        except Exception as error:
            mensaje_asistente = {
                "rol": "assistant",
                "texto": f"Ocurrió un error ({type(error).__name__}): {error}",
            }

    conversacion["mensajes"].append(mensaje_asistente)
    mostrar_mensaje(mensaje_asistente)

# --- Barra lateral: lista de conversaciones y detalles del pipeline ---
with st.sidebar:
    if st.button("➕ Nueva conversación", use_container_width=True):
        # Si la activa ya está vacía, no tiene sentido crear otra
        if conversacion["mensajes"]:
            crear_conversacion()
            st.rerun()

    st.subheader("Conversaciones")
    for id_conv, conv in reversed(list(st.session_state.conversaciones.items())):
        es_activa = id_conv == st.session_state.conversacion_activa
        if st.button(
            conv["titulo"],
            key=f"conv_{id_conv}",
            type="primary" if es_activa else "secondary",
            use_container_width=True,
        ):
            st.session_state.conversacion_activa = id_conv
            st.rerun()

    st.divider()
    st.subheader("Detalles del pipeline")

    ultimo = next(
        (m for m in reversed(conversacion["mensajes"]) if m.get("categoria")),
        None,
    )
    if ultimo:
        st.write(f"**Categoría:** {ultimo['categoria']}")
        st.write(f"**Confianza del clasificador:** {ultimo['confianza']:.2f}")
        if ultimo["chunks"]:
            st.write("**Chunks recuperados:**")
            for chunk in ultimo["chunks"]:
                st.write(f"- {chunk['modelo']}")
    else:
        st.caption("Hacé una pregunta para ver cómo se enruta.")