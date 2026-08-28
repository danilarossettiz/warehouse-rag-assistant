"""
Extrae la documentación de dbt (manifest.json + catalog.json)
y la convierte en chunks de texto legible para el RAG.
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------
# 1. Cargar los archivos generados por dbt
# ---------------------------------------------------------
with open("target/manifest.json") as f:
    manifest = json.load(f)

with open("target/catalog.json") as f:
    catalog = json.load(f)


# ---------------------------------------------------------
# 2. Armar el diccionario de relaciones (foreign keys)
# ---------------------------------------------------------
def extraer_nombre_modelo(texto_ref):
    """
    Los tests de relationships guardan el modelo como:
    "{{ get_where_subquery(ref('stg_olist__order_items')) }}"
    Esta función saca solo el nombre: stg_olist__order_items
    """
    match = re.search(r"ref\('([^']+)'\)", texto_ref)
    return match.group(1) if match else None


relaciones_por_modelo = {}

for node_id, node in manifest["nodes"].items():
    if node["resource_type"] != "test":
        continue
    if "relationships" not in node_id:
        continue

    kwargs = node.get("test_metadata", {}).get("kwargs", {})
    modelo_origen = extraer_nombre_modelo(kwargs.get("model", ""))
    modelo_destino = extraer_nombre_modelo(kwargs.get("to", ""))

    if not modelo_origen or not modelo_destino:
        continue

    relaciones_por_modelo.setdefault(modelo_origen, []).append({
        "columna": kwargs.get("column_name"),
        "apunta_a_modelo": modelo_destino,
        "apunta_a_columna": kwargs.get("field"),
    })


# ---------------------------------------------------------
# 3. Recorrer los modelos y armar un chunk de texto por cada uno
# ---------------------------------------------------------
chunks = []

for node_id, node in manifest["nodes"].items():
    if node["resource_type"] != "model":
        continue

    nombre_modelo = node["name"]
    descripcion = node.get("description", "").strip()

    # La capa (staging / intermediate / marts) sale del fqn,
    # que es la ruta lógica del modelo dentro del proyecto
    fqn = node.get("fqn", [])
    capa = fqn[1] if len(fqn) > 1 else "desconocida"

    # Tipos de dato reales, desde el catalog (columnas en MAYÚSCULAS)
    columnas_catalog = {}
    if node_id in catalog["nodes"]:
        columnas_catalog = {
            col_name.lower(): col_info["type"]
            for col_name, col_info in catalog["nodes"][node_id]["columns"].items()
        }

    # Armamos el texto de cada columna: nombre, tipo y descripción
    lineas_columnas = []
    for col_name, col_info in node.get("columns", {}).items():
        tipo = columnas_catalog.get(col_name.lower(), "tipo desconocido")
        desc_columna = col_info.get("description", "").strip() or "sin descripción"
        lineas_columnas.append(f"  - {col_name} ({tipo}): {desc_columna}")

    texto_columnas = "\n".join(lineas_columnas) if lineas_columnas else "  (sin columnas documentadas)"

    # Armamos el texto de relaciones, si el modelo tiene alguna
    relaciones = relaciones_por_modelo.get(nombre_modelo, [])
    if relaciones:
        lineas_relaciones = [
            f"  - {r['columna']} se relaciona con {r['apunta_a_modelo']}.{r['apunta_a_columna']}"
            for r in relaciones
        ]
        texto_relaciones = "\n".join(lineas_relaciones)
    else:
        texto_relaciones = "  (sin relaciones documentadas)"

    # Armamos el texto de lineage (de qué modelos depende), vía depends_on.nodes.
    # Esto es distinto de "Relaciones": no son foreign keys, es de dónde se construye el modelo.
    nodos_de_los_que_depende = node.get("depends_on", {}).get("nodes", [])
    modelos_de_los_que_depende = [
        manifest["nodes"][dep_id]["name"]
        for dep_id in nodos_de_los_que_depende
        if dep_id.startswith("model.") and dep_id in manifest["nodes"]
    ]
    if modelos_de_los_que_depende:
        texto_depende_de = "\n".join(f"  - {m}" for m in modelos_de_los_que_depende)
    else:
        texto_depende_de = "  (no depende de otros modelos)"

    # Armamos el chunk final, en texto natural
    chunk_text = f"""Modelo: {nombre_modelo}
Capa: {capa}
Descripción: {descripcion or 'sin descripción'}

Columnas:
{texto_columnas}

Relaciones:
{texto_relaciones}

Depende de:
{texto_depende_de}
"""

    chunks.append({
        "model": nombre_modelo,
        "chunk_text": chunk_text,
        "metadata": {
            "layer": capa,
            "database": node.get("database"),
            "schema": node.get("schema"),
        },
    })


# ---------------------------------------------------------
# 4. Guardar el resultado
# ---------------------------------------------------------
output_path = Path("data/dbt_docs_chunks.json")
output_path.parent.mkdir(exist_ok=True)

with open(output_path, "w") as f:
    json.dump(chunks, f, indent=2, ensure_ascii=False)

print(f"Se generaron {len(chunks)} chunks.")
print(f"Guardado en: {output_path}")
print("\n--- Ejemplo del primer chunk ---\n")
print(chunks[0]["chunk_text"])
