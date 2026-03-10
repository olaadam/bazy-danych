use("medical")

db.createCollection("patients")
db.createCollection("doctors")
db.createCollection("departments")
db.createCollection("rooms")
db.createCollection("admin_staff")
db.createCollection("drugs")
db.createCollection("visits")
db.createCollection("medical_records")
db.createCollection("prescriptions")
db.createCollection("diagnostics")

db.patients.createIndex({ pesel: 1 }, { unique: true })

db.visits.createIndex({ patient_id: 1 })
db.visits.createIndex({ doctor_id: 1 })

db.medical_records.createIndex({ patient_id: 1 })

db.prescriptions.createIndex({ patient_id: 1 })
db.prescriptions.createIndex({ doctor_id: 1 })

db.diagnostics.createIndex({ patient_id: 1 })