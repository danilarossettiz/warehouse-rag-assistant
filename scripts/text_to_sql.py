import os
import requests
from dotenv import load_dotenv     
from scripts.load_to_snowflake import get_connection


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
    date_trunc('month', order_purchase_timestamp) as mes,
    sum(payment_value) as ingreso_total
from int_orders__enriched
where year(order_purchase_timestamp) = 2018
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

def llamar_gemini(prompt: str) -> str:                # NUEVO
    response = requests.post(
        f"{API_URL}?key={API_KEY}",
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    texto = data["candidates"][0]["content"]["parts"][0]["text"]
    return texto

def extraer_sql(respuesta: str) -> str:
    partes = respuesta.split("```sql")
    sql_y_resto = partes[1]
    sql_limpio = sql_y_resto.split("```")[0]
    return sql_limpio.strip()
    

def ejecutar_sql(query: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            resultados = cur.fetchall()
    return resultados
