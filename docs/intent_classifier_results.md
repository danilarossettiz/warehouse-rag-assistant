# Resultados del clasificador de intencion

Generado automaticamente por `scripts/train_intent_classifier.py` el 2026-09-13 10:15.

Vocabulario TF-IDF: 535 palabras.

## Comparacion de modelos

| Modelo | Accuracy | Errores en test (de 48) |
|---|---|---|
| Logistic Regression | 93.75% | 3 |
| Naive Bayes | 95.83% | 2 |

---

## Logistic Regression

**Accuracy: 93.75%**

| Categoria | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| definicion | 0.88 | 0.94 | 0.91 | 16 |
| fuera_de_alcance | 0.93 | 0.88 | 0.90 | 16 |
| metrica | 1.00 | 1.00 | 1.00 | 16 |
| **accuracy** | | | **0.94** | 48 |
| macro avg | 0.94 | 0.94 | 0.94 | 48 |
| weighted avg | 0.94 | 0.94 | 0.94 | 48 |

**Matriz de confusion** (filas=real, columnas=prediccion)

| real \ prediccion | definicion | fuera_de_alcance | metrica |
|---|---|---|---|
| **definicion** | 15 | 1 | 0 |
| **fuera_de_alcance** | 2 | 14 | 0 |
| **metrica** | 0 | 0 | 16 |

**Casos mal clasificados (3):**

- real=`fuera_de_alcance` | prediccion=`definicion`
  > estoy aburrido, dame un dato curioso que no sepa
- real=`fuera_de_alcance` | prediccion=`definicion`
  > ¿podrias redactar un correo para pedir disculpas por un retraso en un pedido?
- real=`definicion` | prediccion=`fuera_de_alcance`
  > podrias explicar el significado de 'review_comment_message'?

---

## Naive Bayes

**Accuracy: 95.83%**

| Categoria | Precision | Recall | F1-score | Support |
|---|---|---|---|---|
| definicion | 0.89 | 1.00 | 0.94 | 16 |
| fuera_de_alcance | 1.00 | 0.88 | 0.93 | 16 |
| metrica | 1.00 | 1.00 | 1.00 | 16 |
| **accuracy** | | | **0.96** | 48 |
| macro avg | 0.96 | 0.96 | 0.96 | 48 |
| weighted avg | 0.96 | 0.96 | 0.96 | 48 |

**Matriz de confusion** (filas=real, columnas=prediccion)

| real \ prediccion | definicion | fuera_de_alcance | metrica |
|---|---|---|---|
| **definicion** | 16 | 0 | 0 |
| **fuera_de_alcance** | 2 | 14 | 0 |
| **metrica** | 0 | 0 | 16 |

**Casos mal clasificados (2):**

- real=`fuera_de_alcance` | prediccion=`definicion`
  > estoy aburrido, dame un dato curioso que no sepa
- real=`fuera_de_alcance` | prediccion=`definicion`
  > ¿podrias redactar un correo para pedir disculpas por un retraso en un pedido?
