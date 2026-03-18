import argparse
import json
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql
from psycopg2.extras import execute_values

try:
    from loaders.common import TABLES_IN_LOAD_ORDER, add_shared_dataset_args, resolve_data_dir
except ModuleNotFoundError:
    from common import TABLES_IN_LOAD_ORDER, add_shared_dataset_args, resolve_data_dir


def _read_json_records(data_dir: Path, table: str) -> list[dict]:
    file_path = data_dir / f"{table}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Brak pliku: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    if not isinstance(records, list):
        raise ValueError(f"Plik {file_path} musi zawierac tablice JSON.")

    return records


def _truncate_tables(cur, schema: str) -> None:
    for table in TABLES_IN_LOAD_ORDER:
        truncate_query = sql.SQL("TRUNCATE TABLE {}.{} RESTART IDENTITY CASCADE").format(
            sql.Identifier(schema),
            sql.Identifier(table),
        )
        cur.execute(truncate_query)


def _insert_batch(cur, conn, schema: str, table: str, records: list[dict], page_size: int) -> None:
    if not records:
        return

    columns = list(records[0].keys())
    rows = [tuple(record[column] for column in columns) for record in records]

    insert_query = sql.SQL("INSERT INTO {}.{} ({}) VALUES %s").format(
        sql.Identifier(schema),
        sql.Identifier(table),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    execute_values(cur, insert_query.as_string(conn), rows, page_size=page_size)


def load_postgresql_dataset(
    data_dir: Path,
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
    schema: str,
    batch_size: int,
) -> None:
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=database,
    )

    try:
        with conn:
            with conn.cursor() as cur:
                _truncate_tables(cur, schema)

                for table in TABLES_IN_LOAD_ORDER:
                    records = _read_json_records(data_dir, table)
                    _insert_batch(cur, conn, schema, table, records, batch_size)
                    print(f"[PostgreSQL] Zaladowano {table}: {len(records)} rekordow")
    finally:
        conn.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ladowanie danych JSON do PostgreSQL")
    add_shared_dataset_args(parser)

    parser.add_argument("--host", default=os.getenv("PGHOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PGPORT", "5432")))
    parser.add_argument("--user", default=os.getenv("PGUSER", "admin"))
    parser.add_argument("--password", default=os.getenv("PGPASSWORD", "admin"))
    parser.add_argument("--database", default=os.getenv("PGDATABASE", "medical"))
    parser.add_argument("--schema", default=os.getenv("PGSCHEMA", "medical"))
    parser.add_argument("--batch-size", type=int, default=1000)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.size, args.data_dir)

    load_postgresql_dataset(
        data_dir=data_dir,
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
        schema=args.schema,
        batch_size=args.batch_size,
    )

    print(f"[PostgreSQL] Zakonczono import z katalogu: {data_dir}")


if __name__ == "__main__":
    main()

