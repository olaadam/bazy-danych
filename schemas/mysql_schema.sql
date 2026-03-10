CREATE DATABASE IF NOT EXISTS medical;
USE medical;

CREATE TABLE patients (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    pesel VARCHAR(11) UNIQUE,
    birth_date DATE,
    address TEXT,
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE doctors (
    doctor_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    specialization VARCHAR(100),
    license_number VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100)
);

CREATE TABLE departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    location VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    room_number VARCHAR(20),
    type VARCHAR(50),
    floor INT
);

CREATE TABLE admin_staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    position VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE drugs (
    drug_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    manufacturer VARCHAR(100),
    active_ingredients TEXT,
    form VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE visits (
    visit_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    visit_date DATETIME,
    visit_type VARCHAR(50),
    status VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE medical_records (
    record_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    description TEXT,
    diagnosis TEXT,
    recommendations TEXT,
    created_at DATETIME,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);

CREATE TABLE prescriptions (
    prescription_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    issue_date DATE,
    status VARCHAR(50),
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE diagnostics (
    diagnostic_id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    type VARCHAR(50),
    result TEXT,
    date DATE,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
);