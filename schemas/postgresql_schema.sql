CREATE SCHEMA IF NOT EXISTS medical;
SET search_path TO medical;

CREATE TABLE patients (
    patient_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    pesel VARCHAR(11) UNIQUE,
    birth_date DATE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE doctors (
    doctor_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialization VARCHAR(100),
    license_number VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE departments (
    department_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE rooms (
    room_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    room_number VARCHAR(20),
    type VARCHAR(50),
    floor INT
);

CREATE TABLE admin_staff (
    staff_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE drugs (
    drug_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100),
    manufacturer VARCHAR(100),
    active_ingredients TEXT,
    form VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE visits (
    visit_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    visit_date TIMESTAMP,
    visit_type VARCHAR(50),
    status VARCHAR(50),
    CONSTRAINT fk_visits_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT fk_visits_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE medical_records (
    record_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id INT,
    description TEXT,
    diagnosis TEXT,
    recommendations TEXT,
    created_at TIMESTAMP,
    CONSTRAINT fk_records_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE prescriptions (
    prescription_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    issue_date DATE,
    status VARCHAR(50),
    CONSTRAINT fk_prescriptions_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    CONSTRAINT fk_prescriptions_doctor FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE diagnostics (
    diagnostic_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    patient_id INT,
    type VARCHAR(50),
    result TEXT,
    date DATE,
    CONSTRAINT fk_diagnostics_patient FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

-- CREATE INDEX idx_visits_patient_id ON visits(patient_id);
-- CREATE INDEX idx_visits_doctor_id ON visits(doctor_id);
-- CREATE INDEX idx_medical_records_patient_id ON medical_records(patient_id);
-- CREATE INDEX idx_prescriptions_patient_id ON prescriptions(patient_id);
-- CREATE INDEX idx_prescriptions_doctor_id ON prescriptions(doctor_id);
-- CREATE INDEX idx_diagnostics_patient_id ON diagnostics(patient_id);

