"""
Modulo de intent classification, listo para integrarse al pipeline.

Expone clasificar(pregunta) -> categoria ("metrica" | "definicion" |
"fuera_de_alcance"), cargando el modelo y el vectorizador serializados
una sola vez (carga perezosa, mismo patron que retrieve() en
retrieval.py) y reusandolos en llamadas posteriores.

Requiere haber corrido antes scripts/train_final_intent_model.py, que
genera los archivos en models/.
"""

import unicodedata
from pathlib import Path

import joblib

MODELS_DIR = Path("models")
VECTORIZER_PATH = MODELS_DIR / "intent_vectorizer.joblib"
MODEL_PATH = MODELS_DIR / "intent_classifier.joblib"

_vectorizer = None
_modelo = None


def _limpiar_texto(texto: str) -> str:
    """Misma limpieza usada en preprocess_intent_dataset.py: minusculas
    y sin acentos. Tiene que coincidir exactamente con la limpieza usada
    al entrenar, o el vectorizador ve texto en un formato distinto al
    que aprendio."""
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = " ".join(texto.split())
    return texto


def _cargar_modelos():
    global _vectorizer, _modelo
    if _vectorizer is None or _modelo is None:
        if not VECTORIZER_PATH.exists() or not MODEL_PATH.exists():
            raise FileNotFoundError(
                "No se encontraron los archivos del modelo en 'models/'. "
                "Corre primero scripts/train_final_intent_model.py."
            )
        _vectorizer = joblib.load(VECTORIZER_PATH)
        _modelo = joblib.load(MODEL_PATH)


def clasificar(pregunta: str) -> str:
    """Clasifica una pregunta en "metrica", "definicion" o
    "fuera_de_alcance"."""
    _cargar_modelos()
    texto_limpio = _limpiar_texto(pregunta)
    vector = _vectorizer.transform([texto_limpio])
    prediccion = _modelo.predict(vector)[0]
    return prediccion


if __name__ == "__main__":
    ejemplos = [
        "¿Cuál fue el ingreso total en enero de 2018?",
        "¿Qué significa la columna order_status?",
        "¿Qué tiempo hace hoy?",
    ]
    for pregunta in ejemplos:
        print(f"{clasificar(pregunta):>18}  <-  {pregunta}")
