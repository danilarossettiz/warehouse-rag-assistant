from scripts.text_to_sql import generar_y_ejecutar

CONTEXTO_INGRESO = """
tabla fct_monthly_revenue (grano: una fila por order_purchase_month)
Ingreso = sum(price + freight_value) de los items de pedido, atribuido al mes de compra,
excluyendo pedidos "canceled" o "unavailable". Es ingreso, no ganancia.
columnas:
- order_purchase_month: primer día del mes calendario
- total_orders: cantidad de pedidos distintos en ese mes
- total_revenue: ingreso total del mes
- avg_revenue_per_order: total_revenue / total_orders
"""

CONTEXTO_CATEGORIAS = """
tabla fct_product_category_performance (grano: una fila por product_category)
Rankeada por cantidad de pedidos distintos, excluyendo pedidos "canceled" o "unavailable".
columnas:
- product_category: nombre de categoría de producto (en inglés)
- total_orders: cantidad de pedidos distintos con al menos un item de esta categoría
- total_items: cantidad total de items vendidos en esta categoría
- total_revenue: ingreso total de la categoría (no ganancia)
- orders_rank: ranking por total_orders, descendente (1 = más pedidos)
Para "top N categorías por cantidad de pedidos", filtrar orders_rank <= N.
NO existe ningún ranking por ingreso (revenue_rank) - solo por cantidad de pedidos.
"""

CONTEXTO_ENTREGA = """
tabla int_orders__enriched (grano: una fila por order_id)
columnas:
- order_id, customer_id, customer_unique_id, customer_city, customer_state
- order_status
- order_purchase_at, order_approved_at, order_delivered_carrier_at, order_delivered_customer_at, order_estimated_delivery_at
- is_delivered: booleano
- delivery_days: días fraccionarios entre compra y entrega, ya calculado
"""

PREGUNTAS = [
    ("¿Cuál fue el ingreso total en marzo de 2018?", CONTEXTO_INGRESO),
    ("¿Cuál fue el ingreso promedio por pedido en 2018?", CONTEXTO_INGRESO),
    ("¿Cuáles son las 10 categorías más vendidas por cantidad de pedidos?", CONTEXTO_CATEGORIAS),
    ("¿Cuál es la categoría con más ingresos?", CONTEXTO_CATEGORIAS),
    ("¿Cuántos pedidos se hicieron en cada categoría del top 3?", CONTEXTO_CATEGORIAS),
    ("¿Cuál es el estado con mayor tiempo de entrega?", CONTEXTO_ENTREGA),
    ("¿Cuál es el estado con menor tiempo de entrega promedio?", CONTEXTO_ENTREGA),
]

if __name__ == "__main__":
    exitosas = 0
    for i, (pregunta, contexto) in enumerate(PREGUNTAS, start=1):
        print(f"\n{'=' * 60}")
        print(f"Pregunta {i}: {pregunta}")
        print("=" * 60)
        sql, resultado = generar_y_ejecutar(pregunta, contexto)
        print(f"\nResultado: {resultado}")
        if "No pude generar" not in resultado:
            exitosas += 1

    print(f"\n\n{'#' * 60}")
    print(f"RESUMEN: {exitosas}/{len(PREGUNTAS)} preguntas resueltas exitosamente")
    print("#" * 60)
