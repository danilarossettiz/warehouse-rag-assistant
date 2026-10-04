"""
scripts/eval/evaluar_sistema.py

Corre el set de evaluación completo por responder() y compara contra lo
esperado. Se ejecuta con: python3 -m scripts.eval.evaluar_sistema

- Métricas: se ejecuta la query de referencia y se comparan los datos
  (no el SQL). Se repiten REPETICIONES_METRICA veces por la variación
  del generador de SQL.
- Definiciones: se verifica la categoría y que el chunk esperado haya
  sido recuperado. El contenido de la respuesta se revisa a mano.
- Fuera de alcance: se verifica la categoría y que no se haya generado SQL.
"""

import csv
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from scripts.orquestador import responder
from scripts.text_to_sql import ejecutar_sql

REPETICIONES_METRICA = 3
RUTA_RESULTADOS = Path("docs/evaluacion_resultados.csv")

SET_EVALUACION = [
    # --- Anclas ---
    {"id": "A1", "grupo": "ancla", "categoria": "metrica",
     "pregunta": "¿Cuál fue el ingreso total por mes en 2018?",
     "sql_referencia": """
        select order_purchase_month, total_revenue
        from fct_monthly_revenue
        where order_purchase_month between '2018-01-01' and '2018-12-01'""",
     "ordenado": False},
    {"id": "A2", "grupo": "ancla", "categoria": "metrica",
     "pregunta": "¿Cuáles son las 5 categorías de productos más vendidas por cantidad de pedidos?",
     "sql_referencia": """
        select product_category, total_orders
        from fct_product_category_performance
        where orders_rank <= 5
        order by orders_rank""",
     "ordenado": True},
    {"id": "A3", "grupo": "ancla", "categoria": "metrica",
     "pregunta": "¿Cuál es el tiempo promedio de entrega por estado de Brasil?",
     "sql_referencia": """
        select customer_state, avg_delivery_days
        from fct_delivery_time_by_state""",
     "ordenado": False},
    {"id": "A4", "grupo": "ancla", "categoria": "definicion",
     "pregunta": 'Qué significa el estado de pedido "shipped" en nuestro modelo de datos?',
     "modelo_esperado": "stg_olist__orders"},
    {"id": "A5", "grupo": "ancla", "categoria": "definicion",
     "pregunta": '¿Cómo se calcula el "review_score" de un pedido?',
     "modelo_esperado": "stg_olist__order_reviews"},
    {"id": "A6", "grupo": "ancla", "categoria": "fuera_de_alcance",
     "pregunta": "¿Cuál va a ser el clima mañana en San Pablo?"},
    {"id": "A7", "grupo": "ancla", "categoria": "fuera_de_alcance",
     "pregunta": "¿Podés recomendarme qué producto comprar para un regalo de cumpleaños?"},

    # --- Métricas nuevas ---
    {"id": "M1", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuál fue el ingreso total en marzo de 2018?",
     "sql_referencia": """
        select total_revenue from fct_monthly_revenue
        where order_purchase_month = '2018-03-01'""",
     "ordenado": False},
    {"id": "M2", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuáles son las 10 categorías más vendidas por cantidad de pedidos?",
     "sql_referencia": """
        select product_category, total_orders
        from fct_product_category_performance
        where orders_rank <= 10
        order by orders_rank""",
     "ordenado": True},
    {"id": "M3", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuál es la categoría con más ingresos?",
     "sql_referencia": """
        select product_category, total_revenue
        from fct_product_category_performance
        order by total_revenue desc limit 1""",
     "ordenado": True},
    {"id": "M4", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuál es el estado con mayor tiempo de entrega?",
     "sql_referencia": """
        select customer_state, avg_delivery_days
        from fct_delivery_time_by_state
        order by avg_delivery_days desc limit 1""",
     "ordenado": True},
    {"id": "M5", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuál es el estado con menor tiempo de entrega promedio?",
     "sql_referencia": """
        select customer_state, avg_delivery_days
        from fct_delivery_time_by_state
        order by avg_delivery_days asc limit 1""",
     "ordenado": True},
    {"id": "M6", "grupo": "metrica_nueva", "categoria": "metrica",
     "pregunta": "¿Cuántos pedidos hubo en total en 2017?",
     "sql_referencia": """
        select sum(total_orders) from fct_monthly_revenue
        where order_purchase_month between '2017-01-01' and '2017-12-01'""",
     "ordenado": False},

    # --- Definiciones nuevas ---
    {"id": "D1", "grupo": "definicion_nueva", "categoria": "definicion",
     "pregunta": "¿Qué significa la columna delivery_days?",
     "modelo_esperado": "int_orders__enriched"},
    {"id": "D2", "grupo": "definicion_nueva", "categoria": "definicion",
     "pregunta": "¿Qué es avg_revenue_per_order?",
     "modelo_esperado": "fct_monthly_revenue"},
    {"id": "D3", "grupo": "definicion_nueva", "categoria": "definicion",
     "pregunta": "¿Qué indica orders_rank en el desempeño por categoría?",
     "modelo_esperado": "fct_product_category_performance"},

    # --- Fuera de alcance, casos límite ---
    {"id": "F1", "grupo": "limite", "categoria": "fuera_de_alcance",
     "pregunta": "¿Cuánto va a vender Olist el año que viene?"},
    {"id": "F2", "grupo": "limite", "categoria": "fuera_de_alcance",
     "pregunta": "¿Cuál es el precio del dólar hoy?"},
    {"id": "F3", "grupo": "limite", "categoria": "fuera_de_alcance",
     "pregunta": "¿Cuáles son los mejores productos para regalar?"},

    # --- Variante corta de M1 ---
    {"id": "V1", "grupo": "variante_corta", "categoria": "metrica",
     "pregunta": "ingreso marzo 2018",
     "sql_referencia": """
        select total_revenue from fct_monthly_revenue
        where order_purchase_month = '2018-03-01'""",
     "ordenado": False},
]


def _normalizar_valor(valor):
    """Los números se redondean a 2 decimales; el resto se compara como texto."""
    if isinstance(valor, (int, float, Decimal)):
        return round(float(valor), 2)
    return str(valor)


def _normalizar_filas(filas, ordenado):
    normales = [tuple(_normalizar_valor(v) for v in fila) for fila in filas]
    return normales if ordenado else sorted(normales, key=repr)


def datos_coinciden(datos, referencia, ordenado) -> bool:
    """Compara solo los valores: ignora nombres de columna y, si la
    pregunta no pide un ranking, también el orden de las filas."""
    if datos is None or referencia is None:
        return False
    return (_normalizar_filas(datos[1], ordenado)
            == _normalizar_filas(referencia[1], ordenado))


def _evaluar_resultado(item, r, referencia):
    """Devuelve True/False según el tipo de pregunta (None si hubo error)."""
    if r is None:
        return None
    categoria = item["categoria"]
    if categoria == "metrica":
        return datos_coinciden(r["datos"], referencia, item["ordenado"])
    if categoria == "definicion":
        modelos = [c["modelo"] for c in (r["chunks_recuperados"] or [])]
        return item["modelo_esperado"] in modelos
    return r["sql"] is None  # fuera de alcance: no debe generar SQL


def main() -> None:
    filas_csv = []

    for item in SET_EVALUACION:
        referencia = None
        if item.get("sql_referencia"):
            referencia = ejecutar_sql(item["sql_referencia"])

        repeticiones = REPETICIONES_METRICA if item["categoria"] == "metrica" else 1

        for intento in range(1, repeticiones + 1):
            print(f"[{item['id']}] intento {intento}/{repeticiones}: {item['pregunta']}")
            try:
                r = responder(item["pregunta"], origen="eval")
                error = ""
            except Exception as e:
                r, error = None, f"{type(e).__name__}: {e}"

            categoria_obtenida = str(r["categoria"]) if r else ""
            filas_csv.append({
                "id": item["id"],
                "grupo": item["grupo"],
                "intento": intento,
                "pregunta": item["pregunta"],
                "categoria_esperada": item["categoria"],
                "categoria_obtenida": categoria_obtenida,
                "categoria_ok": categoria_obtenida == item["categoria"],
                "resultado_ok": _evaluar_resultado(item, r, referencia),
                "sql_generado": r["sql"] if r else "",
                "respuesta": r["respuesta"] if r else "",
                "error": error,
            })

    RUTA_RESULTADOS.parent.mkdir(parents=True, exist_ok=True)
    with open(RUTA_RESULTADOS, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=list(filas_csv[0].keys()))
        escritor.writeheader()
        escritor.writerows(filas_csv)

    _imprimir_resumen(filas_csv)
    print(f"\nResultados guardados en {RUTA_RESULTADOS}")


def _imprimir_resumen(filas_csv) -> None:
    por_grupo = defaultdict(lambda: {"n": 0, "cat_ok": 0, "res_ok": 0})
    for fila in filas_csv:
        for clave in (fila["grupo"], "TOTAL"):
            por_grupo[clave]["n"] += 1
            por_grupo[clave]["cat_ok"] += bool(fila["categoria_ok"])
            por_grupo[clave]["res_ok"] += fila["resultado_ok"] is True

    print("\n" + "=" * 62)
    print(f"{'Grupo':<20}{'Corridas':>9}{'Categoría OK':>15}{'Resultado OK':>15}")
    for grupo, s in por_grupo.items():
        print(f"{grupo:<20}{s['n']:>9}{s['cat_ok']:>15}{s['res_ok']:>15}")

    print("\nConsistencia de las métricas (resultado correcto / repeticiones):")
    por_pregunta = defaultdict(lambda: [0, 0])
    for fila in filas_csv:
        if fila["categoria_esperada"] == "metrica":
            por_pregunta[fila["id"]][1] += 1
            por_pregunta[fila["id"]][0] += fila["resultado_ok"] is True
    for id_pregunta, (ok, total) in por_pregunta.items():
        print(f"  {id_pregunta}: {ok}/{total}")


if __name__ == "__main__":
    main()