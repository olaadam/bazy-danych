import json
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# ilość rekordów łącznie
total_records = 5000000

# folder docelowy
data_dir = f"data/{total_records}"
os.makedirs(data_dir, exist_ok=True)

fake = Faker("pl_PL")

# proporcje danych do wygenerowania
NUM_PATIENTS = 1250000
NUM_DOCTORS = 93750
NUM_DEPARTMENTS = 6250
NUM_ROOMS = 56250
NUM_ADMIN = 62500
NUM_DRUGS = 125000
NUM_VISITS = 1250000
NUM_MEDICAL_RECORDS = 625000
NUM_PRESCRIPTIONS = 937500
NUM_DIAGNOSTICS = 593750


# generowanie danych do JSON
def generate_data():

    patients = []
    for i in range(NUM_PATIENTS):
        patients.append({
            "patient_id": i+1,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "pesel": fake.unique.ssn(),
            "birth_date": str(fake.date_of_birth(minimum_age=0, maximum_age=90)),
            "address": fake.address(),
            "phone": fake.phone_number(),
            "email": fake.email()
        })

    doctors = []
    for i in range(NUM_DOCTORS):
        doctors.append({
            "doctor_id": i+1,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "specialization": fake.job(),
            "license_number": str(fake.random_number(6)),
            "phone": fake.phone_number(),
            "email": fake.email()
        })

    departments = []
    for i in range(NUM_DEPARTMENTS):
        departments.append({
            "department_id": i+1,
            "name": f"Oddział {fake.word()}",
            "location": f"Budynek {random.randint(1,3)}",
            "phone": fake.phone_number()
        })

    rooms = []
    for i in range(NUM_ROOMS):
        rooms.append({
            "room_id": i+1,
            "room_number": str(random.randint(1,200)),
            "type": random.choice(["Gabinet","Sala zabiegowa"]),
            "floor": random.randint(1,5)
        })

    admin_staff = []
    for i in range(NUM_ADMIN):
        admin_staff.append({
            "staff_id": i+1,
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "position": random.choice(["Recepcjonista","Sekretarka"]),
            "phone": fake.phone_number()
        })

    drugs = []
    for i in range(NUM_DRUGS):
        drugs.append({
            "drug_id": i+1,
            "name": fake.word(),
            "manufacturer": fake.company(),
            "active_ingredients": fake.word(),
            "form": random.choice(["Tabletki","Syrop"]),
            "price": round(random.uniform(10,100),2)
        })

    visits = []
    for i in range(NUM_VISITS):
        visits.append({
            "visit_id": i+1,
            "patient_id": random.randint(1, NUM_PATIENTS),
            "doctor_id": random.randint(1, NUM_DOCTORS),
            "visit_date": str(datetime.now()-timedelta(days=random.randint(0,365))),
            "visit_type": random.choice(["Kontrolna","Zabiegowa"]),
            "status": "Zakończona"
        })

    medical_records = []
    for i in range(NUM_MEDICAL_RECORDS):
        medical_records.append({
            "record_id": i+1,
            "patient_id": random.randint(1, NUM_PATIENTS),
            "description": fake.sentence(),
            "diagnosis": fake.sentence(),
            "recommendations": fake.sentence(),
            "created_at": str(datetime.now()-timedelta(days=random.randint(0,365)))
        })

    prescriptions = []
    for i in range(NUM_PRESCRIPTIONS):
        prescriptions.append({
            "prescription_id": i+1,
            "patient_id": random.randint(1, NUM_PATIENTS),
            "doctor_id": random.randint(1, NUM_DOCTORS),
            "issue_date": str(datetime.now()-timedelta(days=random.randint(0,365))),
            "status": "Aktywna"
        })

    diagnostics = []
    for i in range(NUM_DIAGNOSTICS):
        diagnostics.append({
            "diagnostic_id": i+1,
            "patient_id": random.randint(1, NUM_PATIENTS),
            "type": random.choice(["USG","MRI"]),
            "result": fake.sentence(),
            "date": str(datetime.now()-timedelta(days=random.randint(0,365)))
        })

    data = {
        "patients": patients,
        "doctors": doctors,
        "departments": departments,
        "rooms": rooms,
        "admin_staff": admin_staff,
        "drugs": drugs,
        "visits": visits,
        "medical_records": medical_records,
        "prescriptions": prescriptions,
        "diagnostics": diagnostics
    }

    for name, table in data.items():
        with open(os.path.join(data_dir, f"{name}.json"),"w",encoding="utf-8") as f:
            json.dump(table,f,ensure_ascii=False,indent=2)

    print("✅ Dane wygenerowane do JSON")


# import to mysql
def load_mysql(data_dir):

    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="haslo",
        database="medical"
    )
    cur = conn.cursor()

    tables = [
        "patients", "doctors", "departments", "rooms", "admin_staff",
        "drugs", "visits", "medical_records", "prescriptions", "diagnostics"
    ]

    #najpierw wyczyść
    for table in tables:
        cur.execute(f"TRUNCATE TABLE {table};") 

    for table in tables:
        for filename in os.listdir(data_dir):
            if filename.endswith(".json") and filename.startswith(table):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    records = json.load(f)
                for r in records:
                    # budujemy zapytanie INSERT dynamicznie
                    cols = ", ".join(r.keys())
                    vals = ", ".join(["%s"]*len(r))
                    sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
                    cur.execute(sql, tuple(r.values()))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ MySQL OK")


# import to postgres
def load_postgres(data_dir):

    import psycopg2

    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="haslo",
        dbname="medical"
    )
    cur = conn.cursor()

    tables = [
        "patients", "doctors", "departments", "rooms", "admin_staff",
        "drugs", "visits", "medical_records", "prescriptions", "diagnostics"
    ]

    #czyszczenie
    for table in tables:
        cur.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;") 

    for table in tables:
        for filename in os.listdir(data_dir):
            if filename.endswith(".json") and filename.startswith(table):
                filepath = os.path.join(data_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    records = json.load(f)
                for r in records:
                    # budujemy zapytanie INSERT dynamicznie
                    cols = ", ".join(r.keys())
                    vals = ", ".join(["%s"]*len(r))
                    sql = f"INSERT INTO {table} ({cols}) VALUES ({vals})"
                    cur.execute(sql, tuple(r.values()))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ PostgreSQL OK")


# import to mongo
def load_mongo(data_dir):

    from pymongo import MongoClient

    client = MongoClient()
    db = client.medical

    collections = [
    "patients", "doctors", "departments", "rooms", "admin_staff",
    "drugs", "visits", "medical_records", "prescriptions", "diagnostics"
    ]

    for col in collections:
        db[col].delete_many({})

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            table = filename.split("_")[0].split(".")[0]  # np. "patients"
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            db[table].insert_many(records)

    print("✅ MongoDB OK")


# import to redis
def load_redis(data_dir):

    import redis
    r = redis.Redis()

    key_prefixes = {
        "patients":"patient",
        "doctors":"doctor",
        "departments":"department",
        "rooms":"room",
        "admin_staff":"staff",
        "drugs":"drug",
        "visits":"visit",
        "medical_records":"record",
        "prescriptions":"prescription",
        "diagnostics":"diagnostic"
    }

    prefixes = [
    "patient","doctor","department","room","staff",
    "drug","visit","record","prescription","diagnostic"
]

    for prefix in prefixes:
        for key in r.scan_iter(f"{prefix}:*"):
            r.delete(key)

    for filename in os.listdir(data_dir):
        if filename.endswith(".json"):
            table = filename.split("_")[0].split(".")[0]
            prefix = key_prefixes.get(table, table)
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                records = json.load(f)
            for r in records:
                r_id = r.get(f"{table[:-1]}_id")  # np. patient_id
                r_key = f"{prefix}:{r_id}"
                r.set(r_key, json.dumps(r, ensure_ascii=False))

    print("✅ Redis OK")


if __name__ == "__main__":
    data_folder = "data/5000000"
    # ręcznie:
    generate_data()
    # load_mysql(data_dir)
    # load_postgres(data_dir)
    # load_mongo(data_dir)
    # load_redis(data_dir)