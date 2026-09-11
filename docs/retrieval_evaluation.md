# Evaluación mínima de retrieval (Etapa 3)

Resultados de `retrieve(pregunta, k=3)` sobre las 7 preguntas ancla.

Para las preguntas de **Definición**, anotar sí/no según si el chunk
con la respuesta real aparece dentro del top-3.

Para **Métrica** y **Fuera de alcance**, no hay chunk 'correcto' —
anotar si la distancia es notablemente más alta que en las de
Definición (señal útil para el umbral de rechazo del clasificador).

## [Métrica] ¿Cuál fue el ingreso total por mes en 2018?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

- **Resultado 1** (modelo: `fct_monthly_revenue`, distancia: 0.4944)
  ```
  Modelo: fct_monthly_revenue
Capa: marts
Descripción: Ingreso por mes calendario, a través de todos los años del dataset. Ingreso (revenue) se define como sum(price + freight_value) de los items de pedido, atribuido al mes en que se realizó el pedido, excluyendo pedidos con estado "canceled" o "unava...
  ```
- **Resultado 2** (modelo: `fct_delivery_time_by_state`, distancia: 0.8012)
  ```
  Modelo: fct_delivery_time_by_state
Capa: marts
Descripción: Tiempo promedio de entrega (en días desde la compra hasta la entrega al cliente) por estado brasileño del cliente, considerando solo pedidos que efectivamente fueron entregados. Grano: una fila por customer_state.

Columnas:
  - customer_st...
  ```
- **Resultado 3** (modelo: `fct_product_category_performance`, distancia: 0.8585)
  ```
  Modelo: fct_product_category_performance
Capa: marts
Descripción: Rendimiento de categorías de producto, rankeadas por cantidad de pedidos distintos que incluyen esa categoría, excluyendo pedidos con estado "canceled" o "unavailable". Grano: una fila por product_category.
Para responder "¿Cuáles son...
  ```

---

## [Métrica] ¿Cuáles son las 5 categorías de productos más vendidas por cantidad de pedidos?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

- **Resultado 1** (modelo: `fct_product_category_performance`, distancia: 0.2303)
  ```
  Modelo: fct_product_category_performance
Capa: marts
Descripción: Rendimiento de categorías de producto, rankeadas por cantidad de pedidos distintos que incluyen esa categoría, excluyendo pedidos con estado "canceled" o "unavailable". Grano: una fila por product_category.
Para responder "¿Cuáles son...
  ```
- **Resultado 2** (modelo: `int_order_items__enriched`, distancia: 0.4494)
  ```
  Modelo: int_order_items__enriched
Capa: intermediate
Descripción: Una fila por item de pedido, enriquecida con el estado/mes de compra del pedido y el nombre de categoría del producto en inglés. Grano: una fila por (order_id, order_item_id).

Columnas:
  - order_id (TEXT): Foreign key hacia el pedid...
  ```
- **Resultado 3** (modelo: `stg_olist__products`, distancia: 0.5209)
  ```
  Modelo: stg_olist__products
Capa: staging
Descripción: Una fila por producto publicado en el marketplace. `product_name_length` y `product_description_length` se renombraron desde las columnas `_lenght` (mal escritas) de la fuente.

Columnas:
  - product_id (TEXT): Primary key. Identificador único d...
  ```

---

## [Métrica] ¿Cuál es el tiempo promedio de entrega por estado de Brasil?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

- **Resultado 1** (modelo: `fct_delivery_time_by_state`, distancia: 0.2076)
  ```
  Modelo: fct_delivery_time_by_state
Capa: marts
Descripción: Tiempo promedio de entrega (en días desde la compra hasta la entrega al cliente) por estado brasileño del cliente, considerando solo pedidos que efectivamente fueron entregados. Grano: una fila por customer_state.

Columnas:
  - customer_st...
  ```
- **Resultado 2** (modelo: `stg_olist__geolocation`, distancia: 0.6234)
  ```
  Modelo: stg_olist__geolocation
Capa: staging
Descripción: Prefijos de código postal brasileños con lat/lng, ciudad y estado aproximados. No es único por geolocation_zip_code_prefix — un prefijo puede abarcar múltiples puntos lat/lng, así que es una tabla de referencia, no una dimensión con clave en...
  ```
- **Resultado 3** (modelo: `fct_monthly_revenue`, distancia: 0.6570)
  ```
  Modelo: fct_monthly_revenue
Capa: marts
Descripción: Ingreso por mes calendario, a través de todos los años del dataset. Ingreso (revenue) se define como sum(price + freight_value) de los items de pedido, atribuido al mes en que se realizó el pedido, excluyendo pedidos con estado "canceled" o "unava...
  ```

---

## [Definición] ¿Qué significa el estado de pedido "shipped" en nuestro modelo de datos?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

**Notas:** chunk correcto en el top-3, pero sigue sin ser el top-1 — se agregó un cross-reference a stg_olist__orders.order_status en int_orders__enriched e int_order_items__enriched (en vez de duplicar el enum, para no romper single-source-of-truth), lo que subió levemente la distancia de int_orders__enriched (0.4573 → 0.4714) pero no alcanzó para invertir el ranking frente a stg_olist__orders (0.4946, sin cambios). Sigue habiendo competencia semántica con int_orders__enriched.

- **Resultado 1** (modelo: `int_orders__enriched`, distancia: 0.4714)
  ```
  Modelo: int_orders__enriched
Capa: intermediate
Descripción: Una fila por pedido, enriquecida con la ubicación del cliente y la duración de la entrega. Grano: una fila por order_id.

Columnas:
  - order_id (TEXT): Primary key. Identificador único del pedido.
  - customer_id (TEXT): Identificador de...
  ```
- **Resultado 2** (modelo: `stg_olist__orders`, distancia: 0.4946)
  ```
  Modelo: stg_olist__orders
Capa: staging
Descripción: Una fila por pedido realizado en el marketplace de Olist.

Columnas:
  - order_id (TEXT): Primary key. Identificador único del pedido.
  - customer_id (TEXT): Identificador de cliente a nivel pedido.
  - order_status (TEXT): Estado (status) actual...
  ```
- **Resultado 3** (modelo: `int_order_items__enriched`, distancia: 0.5228)
  ```
  Modelo: int_order_items__enriched
Capa: intermediate
Descripción: Una fila por item de pedido, enriquecida con el estado/mes de compra del pedido y el nombre de categoría del producto en inglés. Grano: una fila por (order_id, order_item_id).

Columnas:
  - order_id (TEXT): Foreign key hacia el pedid...
  ```

---

## [Definición] ¿Cómo se calcula el "review_score" de un pedido?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

- **Resultado 1** (modelo: `stg_olist__order_reviews`, distancia: 0.4484)
  ```
  Modelo: stg_olist__order_reviews
Capa: staging
Descripción: Una fila por reseña de cliente dejada para un pedido.

Columnas:
  - review_id (TEXT): Identificador de la reseña. No es una primary key estricta — el mismo review_id puede aparecer para más de un order_id en los datos crudos.
  - order_id...
  ```
- **Resultado 2** (modelo: `fct_product_category_performance`, distancia: 0.5556)
  ```
  Modelo: fct_product_category_performance
Capa: marts
Descripción: Rendimiento de categorías de producto, rankeadas por cantidad de pedidos distintos que incluyen esa categoría, excluyendo pedidos con estado "canceled" o "unavailable". Grano: una fila por product_category.
Para responder "¿Cuáles son...
  ```
- **Resultado 3** (modelo: `stg_olist__orders`, distancia: 0.5570)
  ```
  Modelo: stg_olist__orders
Capa: staging
Descripción: Una fila por pedido realizado en el marketplace de Olist.

Columnas:
  - order_id (TEXT): Primary key. Identificador único del pedido.
  - customer_id (TEXT): Identificador de cliente a nivel pedido.
  - order_status (TEXT): Estado (status) actual...
  ```

---

## [Fuera de alcance] ¿Cuál va a ser el clima mañana en San Pablo?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

**Notas:** distancia alta (0.80+), clara separación respecto a preguntas dentro de alcance — buena señal para el umbral de rechazo.

- **Resultado 1** (modelo: `stg_olist__geolocation`, distancia: 0.8848)
  ```
  Modelo: stg_olist__geolocation
Capa: staging
Descripción: Prefijos de código postal brasileños con lat/lng, ciudad y estado aproximados. No es único por geolocation_zip_code_prefix — un prefijo puede abarcar múltiples puntos lat/lng, así que es una tabla de referencia, no una dimensión con clave en...
  ```
- **Resultado 2** (modelo: `fct_delivery_time_by_state`, distancia: 0.9334)
  ```
  Modelo: fct_delivery_time_by_state
Capa: marts
Descripción: Tiempo promedio de entrega (en días desde la compra hasta la entrega al cliente) por estado brasileño del cliente, considerando solo pedidos que efectivamente fueron entregados. Grano: una fila por customer_state.

Columnas:
  - customer_st...
  ```
- **Resultado 3** (modelo: `stg_olist__order_items`, distancia: 0.9413)
  ```
  Modelo: stg_olist__order_items
Capa: staging
Descripción: Una fila por item (producto/vendedor) dentro de un pedido.

Columnas:
  - order_id (TEXT): Foreign key hacia stg_olist__orders.
  - order_item_id (NUMBER): Número secuencial del item dentro del pedido, empezando en 1.
  - product_id (TEXT): F...
  ```

---

## [Fuera de alcance] ¿Podés recomendarme qué producto comprar para un regalo de cumpleaños?

**¿Correcto? (completar a mano):** [x] Sí   [ ] No

**Notas:** distancia alta (0.80+), clara separación respecto a preguntas dentro de alcance — buena señal para el umbral de rechazo.

- **Resultado 1** (modelo: `fct_product_category_performance`, distancia: 0.8009)
  ```
  Modelo: fct_product_category_performance
Capa: marts
Descripción: Rendimiento de categorías de producto, rankeadas por cantidad de pedidos distintos que incluyen esa categoría, excluyendo pedidos con estado "canceled" o "unavailable". Grano: una fila por product_category.
Para responder "¿Cuáles son...
  ```
- **Resultado 2** (modelo: `stg_olist__product_category_translations`, distancia: 0.8306)
  ```
  Modelo: stg_olist__product_category_translations
Capa: staging
Descripción: Traduce los nombres de categoría de producto del portugués al inglés.

Columnas:
  - product_category_name (TEXT): Primary key. Nombre de categoría de producto en portugués.
  - product_category_name_english (TEXT): Nombre d...
  ```
- **Resultado 3** (modelo: `stg_olist__products`, distancia: 0.8366)
  ```
  Modelo: stg_olist__products
Capa: staging
Descripción: Una fila por producto publicado en el marketplace. `product_name_length` y `product_description_length` se renombraron desde las columnas `_lenght` (mal escritas) de la fuente.

Columnas:
  - product_id (TEXT): Primary key. Identificador único d...
  ```

---
