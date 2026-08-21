# Warehouse RAG Assistant

Asistente conversacional que responde preguntas de negocio en lenguaje natural sobre un data warehouse, combinando tres componentes:

- **RAG** — búsqueda semántica sobre la documentación de dbt
- **Clasificador ML** — modelo de machine learning clásico para clasificar la intención de la pregunta (métrica / definición / fuera de alcance)
- **Text-to-SQL** — generación de SQL vía LLM sobre Snowflake

Proyecto final de la diplomatura en Machine Learning e Inteligencia Artificial.

**Dataset:** [Olist Brazilian E-Commerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle). Se usa para definir el caso de negocio y los tipos de consulta — no para entrenar el LLM.

## Estructura del proyecto

```
.
├── dbt/          # Warehouse: modelos de dbt, transformaciones y documentación
├── rag/          # Búsqueda semántica: embeddings + retrieval sobre la doc de dbt
├── classifier/   # Clasificador de intención (ML clásico)
├── app/          # Capa de integración: enruta preguntas a RAG o a Text-to-SQL
└── docs/         # Documentación del proyecto (decisiones de diseño, notas de evaluación)
```

- **`dbt/`** — Capa de warehouse construida con dbt sobre Snowflake. Incluye modelos, transformaciones y la documentación que después alimenta al RAG.
- **`rag/`** — Búsqueda semántica sobre la documentación de dbt: generación de embeddings y lógica de recuperación.
- **`classifier/`** — Clasificador de intención con ML clásico: determina si la pregunta del usuario es una métrica, una definición, o está fuera de alcance.
- **`app/`** — El asistente en sí: recibe la pregunta, clasifica la intención, decide si usa RAG o Text-to-SQL, y devuelve la respuesta.
- **`docs/`** — Documentación a nivel proyecto (decisiones de diseño, resultados de evaluación). No confundir con la documentación de dbt, que vive dentro de `dbt/`.

## Roadmap

El proyecto está organizado en 7 etapas: Setup → Warehouse → RAG → Clasificador ML → Text-to-SQL → Integración → Evaluación.

## Estado

🚧 En progreso — etapa de setup del proyecto.
