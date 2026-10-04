"""
Genera candidatos de ejemplos etiquetados para el dataset del clasificador
de intencion (metrica / definicion / fuera_de_alcance).

Llama a la API de Gemini directamente por HTTP (sin el SDK de Google, que
entra en conflicto con la version de protobuf que necesita dbt).

Los candidatos se guardan en data/intent_dataset_candidates.csv para
revision manual. Nada se agrega al dataset final (data/intent_dataset.csv)
sin pasar por esa revision.
"""

import csv
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["GEMINI_API_KEY"]
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
)

OUTPUT_PATH = Path("data/intent_dataset_candidates.csv")
EXAMPLES_PER_BATCH = 20

PROMPTS = {
    "metrica": """
Genera {n} preguntas en espanol que un usuario de negocio le haria a un
asistente conversacional sobre un data warehouse de e-commerce (dataset
Olist: pedidos, clientes, productos, vendedores, pagos, reviews).

Las preguntas deben requerir calcular una metrica o un numero
(sumas, promedios, conteos, porcentajes, comparaciones en el tiempo, etc.).

Varia el estilo: algunas formales, algunas informales, algunas con errores
de tipeo, algunas mezclando palabras en ingles (como "revenue" o "churn").
No numeres las preguntas. Una por linea, sin texto adicional.
""",
    "definicion": """
Genera {n} preguntas en espanol que un usuario de negocio le haria a un
asistente conversacional para entender que significa un concepto, una
columna o una regla de negocio de un data warehouse de e-commerce (dataset
Olist).

Las preguntas deben pedir una definicion o explicacion, NO un numero.
Ejemplo de tema: que es un pedido cancelado, que significa una columna,
como se calcula un estado.

Varia el estilo: algunas formales, algunas informales, algunas con errores
de tipeo, algunas mezclando palabras en ingles.
No numeres las preguntas. Una por linea, sin texto adicional.
""",
    "fuera_de_alcance": """
Genera {n} preguntas en espanol que un usuario le podria escribir a un
asistente conversacional de un data warehouse de e-commerce, pero que NO
tienen nada que ver con los datos del negocio (ni metricas ni definiciones).

Incluye una mezcla de:
- preguntas totalmente ajenas al dominio (clima, chistes, cultura general)
- preguntas que suenan relacionadas al e-commerce pero que el sistema no
  puede responder porque no hay datos para eso (ej. predicciones futuras,
  opiniones, datos que no estan en el warehouse)

Varia el estilo: algunas formales, algunas informales, algunas con errores
de tipeo.
No numeres las preguntas. Una por linea, sin texto adicional.
""",
}


def generar_candidatos(categoria: str, n: int) -> list[str]:
    prompt = PROMPTS[categoria].format(n=n)
    response = requests.post(
        f"{API_URL}?key={API_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    texto = data["candidates"][0]["content"]["parts"][0]["text"]
    lineas = [linea.strip() for linea in texto.splitlines()]
    return [linea for linea in lineas if linea]


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    existe = OUTPUT_PATH.exists()

    with open(OUTPUT_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["question", "label", "reviewed"])

        for categoria in PROMPTS:
            print(f"Generando {EXAMPLES_PER_BATCH} ejemplos para: {categoria}")
            preguntas = generar_candidatos(categoria, EXAMPLES_PER_BATCH)
            for pregunta in preguntas:
                writer.writerow([pregunta, categoria, "no"])
            time.sleep(2)  # margen para no saturar el free tier

    print(f"Listo. Candidatos agregados en {OUTPUT_PATH}")
    print("Revisalos a mano antes de pasarlos al dataset final.")


if __name__ == "__main__":
    main()
