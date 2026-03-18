import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import redis

try:
    from loaders.common import ID_FIELDS, TABLES_IN_LOAD_ORDER, add_shared_dataset_args, resolve_data_dir
except ModuleNotFoundError:
    from common import ID_FIELDS, TABLES_IN_LOAD_ORDER, add_shared_dataset_args, resolve_data_dir


def _read_json_records(data_dir: Path, table: str) -> list[dict]:
    file_path = data_dir / f"{table}.json"
    if not file_path.exists():
        raise FileNotFoundError(f"Brak pliku: {file_path}")

    with file_path.open("r", encoding="utf-8") as handle:
        records = json.load(handle)

    if not isinstance(records, list):
        raise ValueError(f"Plik {file_path} musi zawierac tablice JSON.")

    return records


def _to_redis_mapping(record: dict) -> dict[str, str]:
    mapping = {}
    for key, value in record.items():
        if value is None:
            mapping[key] = ""
        else:
            mapping[key] = str(value)
    return mapping


def _parse_timestamp(value: str) -> float | None:
    if not value:
        return None

    try:
        return datetime.fromisoformat(value).timestamp()
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d").timestamp()
        except ValueError:
            return None


def _clear_namespace(client: redis.Redis, namespace: str, scan_count: int = 1000) -> None:
    pattern = f"{namespace}:*"
    batch = []

    for key in client.scan_iter(match=pattern, count=scan_count):
        batch.append(key)
        if len(batch) >= scan_count:
            client.delete(*batch)
            batch.clear()

    if batch:
        client.delete(*batch)


def _apply_secondary_indexes(pipe, namespace: str, table: str, record: dict) -> None:
    if table == "patients":
        pesel = record.get("pesel")
        if pesel:
            pipe.set(f"{namespace}:idx:patients:pesel:{pesel}", record["patient_id"])

    if table == "visits":
        pipe.sadd(f"{namespace}:idx:visits:patient:{record['patient_id']}", record["visit_id"])
        pipe.sadd(f"{namespace}:idx:visits:doctor:{record['doctor_id']}", record["visit_id"])
        visit_ts = _parse_timestamp(str(record.get("visit_date", "")))
        if visit_ts is not None:
            pipe.zadd(
                f"{namespace}:timeline:visits:patient:{record['patient_id']}",
                {str(record["visit_id"]): visit_ts},
            )
            pipe.zadd(
                f"{namespace}:timeline:visits:doctor:{record['doctor_id']}",
                {str(record["visit_id"]): visit_ts},
            )

    if table == "medical_records":
        pipe.sadd(f"{namespace}:idx:medical_records:patient:{record['patient_id']}", record["record_id"])

    if table == "prescriptions":
        pipe.sadd(
            f"{namespace}:idx:prescriptions:patient:{record['patient_id']}",
            record["prescription_id"],
        )
        pipe.sadd(
            f"{namespace}:idx:prescriptions:doctor:{record['doctor_id']}",
            record["prescription_id"],
        )
        issue_ts = _parse_timestamp(str(record.get("issue_date", "")))
        if issue_ts is not None:
            pipe.zadd(
                f"{namespace}:timeline:prescriptions:patient:{record['patient_id']}",
                {str(record["prescription_id"]): issue_ts},
            )

    if table == "diagnostics":
        pipe.sadd(
            f"{namespace}:idx:diagnostics:patient:{record['patient_id']}",
            record["diagnostic_id"],
        )
        diag_ts = _parse_timestamp(str(record.get("date", "")))
        if diag_ts is not None:
            pipe.zadd(
                f"{namespace}:timeline:diagnostics:patient:{record['patient_id']}",
                {str(record["diagnostic_id"]): diag_ts},
            )


def load_redis_dataset(
    data_dir: Path,
    host: str,
    port: int,
    db: int,
    password: str | None,
    namespace: str,
    batch_size: int,
) -> None:
    client = redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=True,
    )

    _clear_namespace(client, namespace)

    for table in TABLES_IN_LOAD_ORDER:
        records = _read_json_records(data_dir, table)
        id_field = ID_FIELDS[table]

        pipe = client.pipeline(transaction=False)
        operations = 0

        for record in records:
            if id_field not in record:
                raise ValueError(f"Brak pola {id_field} w rekordzie tabeli {table}")

            record_id = record[id_field]
            entity_key = f"{namespace}:{table}:{record_id}"

            pipe.hset(entity_key, mapping=_to_redis_mapping(record))
            pipe.sadd(f"{namespace}:set:{table}", record_id)

            _apply_secondary_indexes(pipe, namespace, table, record)

            operations += 1
            if operations >= batch_size:
                pipe.execute()
                pipe = client.pipeline(transaction=False)
                operations = 0

        if operations:
            pipe.execute()

        print(f"[Redis] Zaladowano {table}: {len(records)} rekordow")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ladowanie danych JSON do Redis")
    add_shared_dataset_args(parser)

    parser.add_argument("--host", default=os.getenv("REDIS_HOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDIS_PORT", "6379")))
    parser.add_argument("--db", type=int, default=int(os.getenv("REDIS_DB", "0")))
    parser.add_argument("--password", default=os.getenv("REDIS_PASSWORD"))
    parser.add_argument("--namespace", default=os.getenv("REDIS_NAMESPACE", "medical"))
    parser.add_argument("--batch-size", type=int, default=1000)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.size, args.data_dir)

    load_redis_dataset(
        data_dir=data_dir,
        host=args.host,
        port=args.port,
        db=args.db,
        password=args.password,
        namespace=args.namespace,
        batch_size=args.batch_size,
    )

    print(f"[Redis] Zakonczono import z katalogu: {data_dir}")


if __name__ == "__main__":
    main()

