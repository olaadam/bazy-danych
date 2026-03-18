import argparse
from pathlib import Path

TABLES_IN_LOAD_ORDER = [
    "patients",
    "doctors",
    "departments",
    "rooms",
    "admin_staff",
    "drugs",
    "visits",
    "medical_records",
    "prescriptions",
    "diagnostics",
]

ID_FIELDS = {
    "patients": "patient_id",
    "doctors": "doctor_id",
    "departments": "department_id",
    "rooms": "room_id",
    "admin_staff": "staff_id",
    "drugs": "drug_id",
    "visits": "visit_id",
    "medical_records": "record_id",
    "prescriptions": "prescription_id",
    "diagnostics": "diagnostic_id",
}

SIZE_ALIASES = {
    "10k": 10000,
    "250k": 250000,
    "500k": 500000,
    "1m": 1000000,
    "5m": 5000000,
    "10m": 10000000,
    "10000": 10000,
    "250000": 250000,
    "500000": 500000,
    "1000000": 1000000,
    "5000000": 5000000,
    "10000000": 10000000,
}


def resolve_data_dir(size: str | None, data_dir: str | None) -> Path:
    if data_dir:
        path = Path(data_dir)
    elif size:
        normalized = size.strip().lower()
        if normalized not in SIZE_ALIASES:
            known = ", ".join(sorted(SIZE_ALIASES.keys()))
            raise ValueError(f"Nieznany rozmiar '{size}'. Dostepne aliasy: {known}")
        path = Path("data") / str(SIZE_ALIASES[normalized])
    else:
        raise ValueError("Podaj --size albo --data-dir.")

    if not path.exists() or not path.is_dir():
        raise FileNotFoundError(f"Katalog danych nie istnieje: {path}")

    return path


def add_shared_dataset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--size",
        type=str,
        default=None,
        help="Alias rozmiaru danych, np. 500k, 1m, 10m.",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=None,
        help="Sciezka do katalogu z plikami JSON (np. data/250000).",
    )

