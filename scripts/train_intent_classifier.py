"""
Entrena y compara dos clasificadores de intencion (baseline):
- TF-IDF + Logistic Regression
- TF-IDF + Naive Bayes

Usa los splits generados por preprocess_intent_dataset.py.

Ademas de imprimir los resultados en la terminal, genera un reporte en
Markdown (docs/intent_classifier_results.md) con las metricas, las
matrices de confusion y los casos mal clasificados de cada modelo,
para que queden documentados sin tener que volver a correr el script.
"""

import csv
from datetime import datetime
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

TRAIN_PATH = Path("data/intent_train.csv")
TEST_PATH = Path("data/intent_test.csv")
REPORT_PATH = Path("docs/intent_classifier_results.md")


def cargar(path: Path):
    with open(path, newline="", encoding="utf-8") as f:
        filas = list(csv.DictReader(f))
    textos = [fila["question_clean"] for fila in filas]
    etiquetas = [fila["label"] for fila in filas]
    return textos, etiquetas


def tabla_classification_report(reporte: dict, etiquetas: list[str]) -> str:
    filas = ["| Categoria | Precision | Recall | F1-score | Support |",
             "|---|---|---|---|---|"]
    for etiqueta in etiquetas:
        m = reporte[etiqueta]
        filas.append(
            f"| {etiqueta} | {m['precision']:.2f} | {m['recall']:.2f} | "
            f"{m['f1-score']:.2f} | {int(m['support'])} |"
        )
    filas.append(
        f"| **accuracy** | | | **{reporte['accuracy']:.2f}** | "
        f"{int(reporte['macro avg']['support'])} |"
    )
    filas.append(
        f"| macro avg | {reporte['macro avg']['precision']:.2f} | "
        f"{reporte['macro avg']['recall']:.2f} | "
        f"{reporte['macro avg']['f1-score']:.2f} | "
        f"{int(reporte['macro avg']['support'])} |"
    )
    filas.append(
        f"| weighted avg | {reporte['weighted avg']['precision']:.2f} | "
        f"{reporte['weighted avg']['recall']:.2f} | "
        f"{reporte['weighted avg']['f1-score']:.2f} | "
        f"{int(reporte['weighted avg']['support'])} |"
    )
    return "\n".join(filas)


def tabla_matriz_confusion(matriz, etiquetas: list[str]) -> str:
    encabezado = "| real \\ prediccion | " + " | ".join(etiquetas) + " |"
    separador = "|---|" + "---|" * len(etiquetas)
    filas = [encabezado, separador]
    for etiqueta_real, fila in zip(etiquetas, matriz):
        valores = " | ".join(str(v) for v in fila)
        filas.append(f"| **{etiqueta_real}** | {valores} |")
    return "\n".join(filas)


def main():
    X_train_texto, y_train = cargar(TRAIN_PATH)
    X_test_texto, y_test = cargar(TEST_PATH)

    vectorizer = TfidfVectorizer()
    X_train = vectorizer.fit_transform(X_train_texto)
    X_test = vectorizer.transform(X_test_texto)

    print(f"Vocabulario aprendido: {len(vectorizer.vocabulary_)} palabras\n")

    modelos = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": MultinomialNB(),
    }

    etiquetas = sorted(set(y_test))
    secciones_md = []
    resumen_comparativo = []

    for nombre, modelo in modelos.items():
        modelo.fit(X_train, y_train)
        predicciones = modelo.predict(X_test)
        acc = accuracy_score(y_test, predicciones)

        print(f"=== {nombre} ===")
        print(f"Accuracy: {acc:.2%}")
        print(classification_report(y_test, predicciones))

        matriz = confusion_matrix(y_test, predicciones, labels=etiquetas)
        print("Matriz de confusion (filas=real, columnas=prediccion):")
        print("            " + "  ".join(f"{e[:10]:>10}" for e in etiquetas))
        for etiqueta_real, fila in zip(etiquetas, matriz):
            print(f"{etiqueta_real[:10]:>10}  " + "  ".join(f"{v:>10}" for v in fila))

        errores = [
            (texto, real, pred)
            for texto, real, pred in zip(X_test_texto, y_test, predicciones)
            if real != pred
        ]
        if errores:
            print(f"\nCasos mal clasificados ({len(errores)}):")
            for texto, real, pred in errores:
                print(f"  real={real} | prediccion={pred}")
                print(f"    {texto}")
        print()

        reporte_dict = classification_report(
            y_test, predicciones, output_dict=True
        )
        resumen_comparativo.append((nombre, acc, len(errores)))

        seccion = [f"## {nombre}\n", f"**Accuracy: {acc:.2%}**\n"]
        seccion.append(tabla_classification_report(reporte_dict, etiquetas))
        seccion.append("\n**Matriz de confusion** (filas=real, columnas=prediccion)\n")
        seccion.append(tabla_matriz_confusion(matriz, etiquetas))

        if errores:
            seccion.append(f"\n**Casos mal clasificados ({len(errores)}):**\n")
            for texto, real, pred in errores:
                seccion.append(f"- real=`{real}` | prediccion=`{pred}`")
                seccion.append(f"  > {texto}")
        secciones_md.append("\n".join(seccion))

    tabla_resumen = [
        "| Modelo | Accuracy | Errores en test (de 48) |",
        "|---|---|---|",
    ]
    for nombre, acc, n_errores in resumen_comparativo:
        tabla_resumen.append(f"| {nombre} | {acc:.2%} | {n_errores} |")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("# Resultados del clasificador de intencion\n\n")
        f.write(
            f"Generado automaticamente por `scripts/train_intent_classifier.py` "
            f"el {datetime.now().strftime('%Y-%m-%d %H:%M')}.\n\n"
        )
        f.write(f"Vocabulario TF-IDF: {len(vectorizer.vocabulary_)} palabras.\n\n")
        f.write("## Comparacion de modelos\n\n")
        f.write("\n".join(tabla_resumen))
        f.write("\n\n---\n\n")
        f.write("\n\n---\n\n".join(secciones_md))
        f.write("\n")

    print(f"Reporte guardado en {REPORT_PATH}")


if __name__ == "__main__":
    main()
