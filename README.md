# Warehouse RAG Assistant

Asistente conversacional que responde preguntas de negocio en lenguaje natural sobre un data warehouse, combinando tres componentes:

- **RAG** — búsqueda semántica sobre la documentación de dbt
- **Clasificador ML** — modelo de machine learning clásico para clasificar la intención de la pregunta (métrica / definición / fuera de alcance)
- **Text-to-SQL** — generación de SQL vía LLM sobre Snowflake

Proyecto final de la diplomatura en Machine Learning e Inteligencia Artificial.

**Dataset:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle). Se eligió por su estructura relacional real (pedidos, productos, clientes, pagos, reviews), su volumen (~100k pedidos, 2016-2018) y porque sus tablas mapean directamente con las preguntas de negocio del proyecto (ventas, tiempos de entrega, categorías). Es importante aclarar que el dataset no se usa para entrenar el LLM ni el clasificador; su función es definir el esquema del warehouse y los tipos de preguntas que el sistema debe poder responder mediante RAG, clasificación de intención y Text-to-SQL.

## Estructura del proyecto

```
.
├── app.py              # Interfaz de chat en Streamlit
├── dbt/                # Warehouse: modelos de dbt, transformaciones y documentación
├── scripts/
│   ├── orquestador.py  # Enruta cada pregunta a RAG o a Text-to-SQL y devuelve la respuesta
│   ├── retrieval.py, classify_intent.py, text_to_sql.py, ...  # Módulos que usa el orquestador
│   ├── pipeline/       # Scripts de una sola corrida: descarga de datos, embeddings, entrenamiento del clasificador
│   └── eval/           # Scripts de evaluación del sistema (RAG, clasificador, pipeline completo)
├── data/               # Datasets, embeddings e índices intermedios
├── models/             # Modelos serializados del clasificador de intención
├── tests/              # Tests automatizados (pytest) del clasificador y el retrieval
└── docs/               # Documentación del proyecto (decisiones de diseño, notas de evaluación)
```

- **`dbt/`** — Capa de warehouse construida con dbt sobre Snowflake. Incluye modelos, transformaciones y la documentación que después alimenta al RAG.
- **`scripts/`** — Toda la lógica de la aplicación: `orquestador.py` conecta clasificador de intención, RAG y Text-to-SQL; `scripts/pipeline/` prepara los datos (dataset, embeddings, entrenamiento); `scripts/eval/` evalúa el sistema.
- **`app.py`** — Interfaz de chat en Streamlit; solo presenta lo que devuelve `responder()` del orquestador.
- **`docs/`** — Documentación a nivel proyecto (decisiones de diseño, resultados de evaluación). No confundir con la documentación de dbt, que vive dentro de `dbt/`.

## Tests

```
pip install -r requirements.txt
python3 -m scripts.pipeline.build_vector_store  # genera chroma_db/ a partir de data/dbt_docs_embeddings.json (no se versiona en git)
pytest
```

Los tests de `tests/test_retrieval.py` necesitan el índice de Chroma en `chroma_db/`; si no existe, se saltan solos con un mensaje explicando cómo generarlo. La primera corrida tarda unos segundos de más porque carga el modelo de embeddings en memoria.

Dos casos están marcados con `xfail` porque documentan defectos conocidos (no arreglados todavía): el clasificador confunde la definición de `orders_rank` con una métrica, y el prefijo de contexto que antepone `orquestador._armar_pregunta_efectiva` a las preguntas de seguimiento degrada el retrieval de `delivery_days`. Si algún día se corrigen, pytest lo va a marcar como fallo (`XPASS`) para que te enteres.

## Roadmap

El proyecto está organizado en 7 etapas: Setup → Warehouse → RAG → Clasificador ML → Text-to-SQL → Integración → Evaluación.

## Estado

✅ Pipeline completo (dbt + RAG + clasificador de intención + Text-to-SQL) integrado en `orquestador.py` y expuesto vía una interfaz de chat en Streamlit (`app.py`). Evaluación end-to-end en curso (`scripts/eval/`).
