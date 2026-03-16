import json
import random
from faker import Faker
from datetime import datetime, timedelta
import os

# ilość rekordów łącznie
total_records = 1000000

# folder docelowy
data_dir = f"data/{total_records}"
os.makedirs(data_dir, exist_ok=True)

fake = Faker("pl_PL")

# proporcje danych do wygenerowania
NUM_PATIENTS = 250000
NUM_DOCTORS = 18750
NUM_DEPARTMENTS = 1250
NUM_ROOMS = 11250
NUM_ADMIN = 12500
NUM_DRUGS = 25000
NUM_VISITS = 250000
NUM_MEDICAL_RECORDS = 125000
NUM_PRESCRIPTIONS = 187500
NUM_DIAGNOSTICS = 118750


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
def load_mysql():

    import mysql.connector

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="haslo",
        database="medical"
    )
    cur = conn.cursor()

    with open("patients.json") as f:
        patients = json.load(f)

    # wczytywanie wszystkich plików JSON w folderze
    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename.startswith("patients"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                patients = json.load(f)
            for p in patients:
                cur.execute(
                    "INSERT INTO patients VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    tuple(p.values())
                )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ MySQL OK")


# import to postgres
def load_postgres():

    import psycopg2

    conn = psycopg2.connect(
        host="localhost",
        user="postgres",
        password="haslo",
        dbname="medical"
    )
    cur = conn.cursor()

    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename.startswith("patients"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                patients = json.load(f)
            for p in patients:
                cur.execute(
                    "INSERT INTO patients VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    tuple(p.values())
                )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ PostgreSQL OK")


# import to mongo
def load_mongo():

    from pymongo import MongoClient

    client = MongoClient()
    db = client.medical

    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename.startswith("patients"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                patients = json.load(f)
            db.patients.insert_many(patients)

    print("✅ MongoDB OK")


# import to redis
def load_redis():

    import redis
    r = redis.Redis()

    for filename in os.listdir(data_dir):
        if filename.endswith(".json") and filename.startswith("patients"):
            filepath = os.path.join(data_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                patients = json.load(f)
            for p in patients:
                r.set(f"patient:{p['patient_id']}", json.dumps(p, ensure_ascii=False))

    print("✅ Redis OK")


if __name__ == "__main__":
    data_folder = "data/1000000"
    # ręcznie:
    generate_data()
    # load_mysql(data_dir)
    # load_postgres(data_dir)
    # load_mongo(data_dir)
    # load_redis(data_dir)