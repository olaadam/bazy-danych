#przyklad
from faker import Faker

fake = Faker("pl_PL")

for i in range(10000):

    patient = (
        fake.first_name(),
        fake.last_name(),
        fake.pesel(),
        fake.date()
    )

    cursor.execute(
    "INSERT INTO patients(first_name,last_name,pesel,birth_date) VALUES (%s,%s,%s,%s)",
    patient
    )