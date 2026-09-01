"""
Loads the Olist raw CSV files into Snowflake:
- Creates schema RAW (if not exists)
- Creates a CSV file format with header parsing
- Creates an internal stage
- Uploads (PUT) all CSVs from data/raw/ to the stage
- Auto-detects each CSV's schema and creates a matching table
- Loads data into each table with COPY INTO

Requires Snowflake credentials in the project .env file:
SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD,
SNOWFLAKE_ROLE, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE
"""

import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

from cryptography.hazmat.primitives import serialization

load_dotenv()

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"
SCHEMA = "RAW"
STAGE = "OLIST_STAGE"
FILE_FORMAT = "CSV_FORMAT"


def table_name_from_file(filename: str) -> str:
    name = filename.replace(".csv", "")
    name = name.replace("olist_", "").replace("_dataset", "")
    return name.upper()


def load_private_key():
    key_path = os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]
    with open(key_path, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        private_key=load_private_key(),
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
    )

def setup_schema_and_stage(cur):
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")
    cur.execute(f"USE SCHEMA {SCHEMA}")
    cur.execute(f"""
        CREATE OR REPLACE FILE FORMAT {FILE_FORMAT}
        TYPE = 'CSV'
        FIELD_DELIMITER = ','
        PARSE_HEADER = TRUE
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF = ('', 'NULL')
        EMPTY_FIELD_AS_NULL = TRUE
    """)
    cur.execute(f"""
        CREATE STAGE IF NOT EXISTS {STAGE}
        FILE_FORMAT = {FILE_FORMAT}
    """)


def upload_files(cur):
    csv_files = sorted(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")
    for csv_file in csv_files:
        print(f"Uploading {csv_file.name} ...")
        cur.execute(
            f"PUT file://{csv_file} @{STAGE} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        )
    return csv_files


def create_and_load_table(cur, csv_file: Path):
    table = table_name_from_file(csv_file.name)
    staged_file = f"@{STAGE}/{csv_file.name}.gz"

    print(f"Inferring schema for {table} ...")
    cur.execute(f"""
        CREATE OR REPLACE TABLE {table}
        USING TEMPLATE (
            SELECT ARRAY_AGG(OBJECT_CONSTRUCT(*))
            FROM TABLE(
                INFER_SCHEMA(
                    LOCATION => '{staged_file}',
                    FILE_FORMAT => '{FILE_FORMAT}'
                )
            )
        )
    """)

    print(f"Loading data into {table} ...")
    cur.execute(f"""
        COPY INTO {table}
        FROM '{staged_file}'
        FILE_FORMAT = (FORMAT_NAME = '{FILE_FORMAT}')
        MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE
    """)

    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"{table}: {count} rows loaded.")


def main():
    conn = get_connection()
    try:
        cur = conn.cursor()
        setup_schema_and_stage(cur)
        csv_files = upload_files(cur)

        for csv_file in csv_files:
            create_and_load_table(cur, csv_file)

        print("All tables loaded successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
