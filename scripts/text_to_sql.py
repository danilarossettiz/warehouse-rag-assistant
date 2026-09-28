import os
import requests
import time
import csv
from decimal import Decimal
from dotenv import load_dotenv
from scripts.load_to_snowflake import get_connection
from snowflake.connector.errors import ProgrammingError
from datetime import datetime

LOG_PATH = "data/text_to_sql_log.csv"


load_dotenv()

API_KEY = os.environ["GEMINI_API_KEY"]
API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3.1-flash-lite:generateContent"
)


def armar_prompt(pregunta_usuario, contexto_rag):
    rol = "Sos un asistente que traduce preguntas en español a consultas SQL para Snowflake. Generá SOLO SQL válido para Snowflake."

    ejemplos = """
Pregunta: "¿Cuál fue el ingreso total por mes en 2018?"
SQL:
select 
    date_trunc('month', order_purchase_at) as mes,
    sum(payment_value) as ingreso_total
from int_orders__enriched
where year(order_purchase_at) = 2018
group by 1
order by 1

Pregunta: "¿Cuáles son las 5 categorías de productos más vendidas por cantidad de pedidos?"
SQL:
select 
    product_category_name,
    count(order_id) as cantidad_pedidos
from int_orders__enriched
group by 1
order by 2 desc
limit 5
"""

    formato_salida = "Devolvé SOLO el SQL, sin explicación, entre bloques ```sql y ```."

    prompt_final = f"""
[ROL]
{rol}

[ESQUEMA]
{contexto_rag}

[EJEMPLOS]
{ejemplos}

[PREGUNTA]
{pregunta_usuario}

[FORMATO DE SALIDA]
{formato_salida}
"""

    return prompt_final


def llamar_gemini(prompt: str, intentos: int = 3) -> str:
    for intento in range(intentos):
        try:
            response = requests.post(
                f"{API_URL}?key={API_KEY}",
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            texto = data["candidates"][0]["content"]["parts"][0]["text"]
            return texto
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as error:
            if intento < intentos - 1:
                espera = 2 ** (intento + 1)
                print(f"Timeout/conexión falló, reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise
        except requests.exceptions.HTTPError as error:
            if response.status_code == 503 and intento < intentos - 1:
                espera = 2 ** (intento + 1)
                print(f"Gemini devolvió 503, reintentando en {espera}s...")
                time.sleep(espera)
            else:
                raise


def extraer_sql(respuesta: str) -> str:
    partes = respuesta.split("```sql")
    sql_y_resto = partes[1]
    sql_limpio = sql_y_resto.split("```")[0]
    return sql_limpio.strip()


def aplicar_limite(query: str, limite: int = 1000) -> str:
    if "limit" in query.lower():
        return query
    return f"{query.rstrip(';')}\nLIMIT {limite}"

def ejecutar_sql(query: str):
    query = aplicar_limite(query)
    with get_connection(role="TEXT_TO_SQL_READONLY") as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            columnas = [col[0] for col in cur.description]
            filas = cur.fetchall()
    return columnas, filas


def formatear_resultado(columnas, filas) -> str:
    if not filas:
        return "No se encontraron resultados."

    if len(filas) == 1 and len(filas[0]) == 1:
        valor = filas[0][0]
        if isinstance(valor, Decimal):
            valor = round(float(valor), 2)
        return f"{columnas[0]}: {valor}"

    lineas = [" | ".join(columnas)]
    for fila in filas:
        fila_texto = []
        for valor in fila:
            if isinstance(valor, Decimal):
                valor = round(float(valor), 2)
            fila_texto.append(str(valor))
        lineas.append(" | ".join(fila_texto))
    return "\n".join(lineas)


def generar_y_ejecutar(pregunta_usuario: str, contexto_rag: str, intentos: int = 2):
    prompt = armar_prompt(pregunta_usuario, contexto_rag)
    error_previo = None
    sql = None

    for intento in range(intentos):
        if error_previo:
            prompt += f"\n\n[ERROR ANTERIOR]\nEl SQL anterior falló con este error de Snowflake:\n{error_previo}\nCorregí el SQL para evitar este error."
        try:
            respuesta = llamar_gemini(prompt)
            sql = extraer_sql(respuesta)
            print(f"SQL generado (intento {intento + 1}): {sql}")
            columnas, filas = ejecutar_sql(sql)
            resultado = formatear_resultado(columnas, filas)
            loggear_corrida(pregunta_usuario, contexto_rag, sql, resultado)
            return sql, resultado
        except ProgrammingError as error:
            print(f"Intento {intento + 1} falló (SQL inválido): {error}")
            error_previo = str(error)
        except requests.exceptions.RequestException as error:
            print(f"Intento {intento + 1} falló (Gemini no respondió): {error}")
            error_previo = None

    resultado = "No pude generar una consulta SQL válida para esa pregunta. ¿Podés reformularla?"
    loggear_corrida(pregunta_usuario, contexto_rag, sql, resultado)
    return sql, resultado


def loggear_corrida(pregunta, contexto_rag, sql, resultado):
    existe = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not existe:
            writer.writerow(["timestamp", "pregunta", "contexto_rag", "sql", "resultado"])
        writer.writerow([datetime.now().isoformat(), pregunta, contexto_rag, sql, resultado])