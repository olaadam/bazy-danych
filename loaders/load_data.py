import argparse

try:
    from loaders.postgresql_loader import load_postgresql_dataset
    from loaders.redis_loader import load_redis_dataset
    from loaders.common import resolve_data_dir
except ModuleNotFoundError:
    from postgresql_loader import load_postgresql_dataset
    from redis_loader import load_redis_dataset
    from common import resolve_data_dir


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Uruchamianie loaderow danych JSON")

    parser.add_argument("--db", choices=["postgresql", "redis"], required=True)
    parser.add_argument("--size", type=str, default=None)
    parser.add_argument("--data-dir", type=str, default=None)

    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--user", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--database", default="medical")
    parser.add_argument("--schema", default="medical")
    parser.add_argument("--namespace", default="medical")
    parser.add_argument("--db-index", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=1000)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data_dir = resolve_data_dir(args.size, args.data_dir)

    if args.db == "postgresql":
        port = args.port if args.port is not None else 5432
        load_postgresql_dataset(
            data_dir=data_dir,
            host=args.host,
            port=port,
            user=args.user,
            password=args.password,
            database=args.database,
            schema=args.schema,
            batch_size=args.batch_size,
        )
        return

    port = args.port if args.port is not None else 6379
    redis_password = args.password if args.password else None
    load_redis_dataset(
        data_dir=data_dir,
        host=args.host,
        port=port,
        db=args.db_index,
        password=redis_password,
        namespace=args.namespace,
        batch_size=args.batch_size,
    )


if __name__ == "__main__":
    main()
