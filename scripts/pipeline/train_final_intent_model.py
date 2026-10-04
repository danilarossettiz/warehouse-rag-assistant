"""
Entrena el modelo final del clasificador de intencion (TF-IDF + Naive
Bayes, elegido tras comparar contra Logistic Regression en
train_intent_classifier.py) y lo serializa junto con el vectorizador.

Se entrena sobre el dataset COMPLETO (train + test combinados, 240
preguntas), no solo sobre el train set. El split train/test ya cumplio
su proposito -- comparar modelos y medir generalizacion -- asi que para
el modelo que va a produccion se aprovechan todos los ejemplos
etiquetados disponibles.

Genera:
  models/intent_vectorizer.joblib
  models/intent_classifier.joblib
"""

import csv
from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

TRAIN_PATH = Path("data/intent_train.csv")
TEST_PATH = Path("data/intent_test.csv")
MODELS_DIR = Path("models")


def cargar(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    textos = [fila["question_clean"] for fila in filas]
    etiquetas = [fila["label"] for fila in filas]
    return textos, etiquetas


def main():
    textos_train, etiquetas_train = cargar(TRAIN_PATH)
    textos_test, etiquetas_test = cargar(TEST_PATH)

    textos = textos_train + textos_test
    etiquetas = etiquetas_train + etiquetas_test
    print(f"Entrenando sobre el dataset completo: {len(textos)} preguntas")

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(textos)

    modelo = MultinomialNB()
    modelo.fit(X, etiquetas)

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, MODELS_DIR / "intent_vectorizer.joblib")
    joblib.dump(modelo, MODELS_DIR / "intent_classifier.joblib")

    print(f"Vectorizador guardado en {MODELS_DIR / 'intent_vectorizer.joblib'}")
    print(f"Modelo guardado en {MODELS_DIR / 'intent_classifier.joblib'}")


if __name__ == "__main__":
    main()
