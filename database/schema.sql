-- Patient Record System - PostgreSQL schema
-- Run with:  psql -U postgres -d patient_records -f database/schema.sql
-- Safe to run more than once (IF NOT EXISTS / OR REPLACE).

CREATE TABLE IF NOT EXISTS patients (
    patient_id     SERIAL PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    gender         VARCHAR(10)  NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    date_of_birth  DATE         NOT NULL CHECK (date_of_birth <= CURRENT_DATE),
    phone          VARCHAR(20)  NOT NULL,
    email          VARCHAR(100),
    address        VARCHAR(200),
    blood_group    VARCHAR(7)   NOT NULL DEFAULT 'Unknown'
                   CHECK (blood_group IN ('A+','A-','B+','B-','AB+','AB-','O+','O-','Unknown')),
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id      SERIAL PRIMARY KEY,
    full_name      VARCHAR(100) NOT NULL,
    gender         VARCHAR(10)  NOT NULL CHECK (gender IN ('Male', 'Female', 'Other')),
    phone          VARCHAR(20)  NOT NULL,
    email          VARCHAR(100),
    specialization VARCHAR(50)  NOT NULL,
    staff_number   VARCHAR(12)  NOT NULL UNIQUE,
    created_at     TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id SERIAL PRIMARY KEY,
    patient_id     INTEGER NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id      INTEGER NOT NULL REFERENCES doctors(doctor_id)  ON DELETE RESTRICT,
    scheduled_at   TIMESTAMP   NOT NULL,
    reason         VARCHAR(200) NOT NULL,
    status         VARCHAR(10) NOT NULL DEFAULT 'Scheduled'
                   CHECK (status IN ('Scheduled', 'Completed', 'Cancelled')),
    -- a doctor cannot have two appointments at the same time
    CONSTRAINT uq_doctor_slot UNIQUE (doctor_id, scheduled_at)
);

CREATE TABLE IF NOT EXISTS medical_records (
    record_id      SERIAL PRIMARY KEY,
    patient_id     INTEGER NOT NULL REFERENCES patients(patient_id) ON DELETE CASCADE,
    doctor_id      INTEGER NOT NULL REFERENCES doctors(doctor_id)  ON DELETE RESTRICT,
    visit_date     DATE    NOT NULL CHECK (visit_date <= CURRENT_DATE),
    diagnosis      VARCHAR(200) NOT NULL,
    treatment      TEXT,
    notes          TEXT
);

-- Indexes on foreign keys and search columns
CREATE INDEX IF NOT EXISTS idx_patients_name       ON patients (full_name);
CREATE INDEX IF NOT EXISTS idx_appointments_patient ON appointments (patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor  ON appointments (doctor_id);
CREATE INDEX IF NOT EXISTS idx_records_patient      ON medical_records (patient_id);

-- Views join the tables so the GUI can show names instead of IDs
CREATE OR REPLACE VIEW v_appointments AS
SELECT a.*, p.full_name AS patient_name, d.full_name AS doctor_name
FROM appointments a
JOIN patients p ON p.patient_id = a.patient_id
JOIN doctors  d ON d.doctor_id  = a.doctor_id;

CREATE OR REPLACE VIEW v_medical_records AS
SELECT r.*, p.full_name AS patient_name, d.full_name AS doctor_name
FROM medical_records r
JOIN patients p ON p.patient_id = r.patient_id
JOIN doctors  d ON d.doctor_id  = r.doctor_id;
