-- Optional sample data (fictional people) for demos and screenshots.
-- psql -U postgres -d patient_records -f database/seed.sql

INSERT INTO doctors (full_name, gender, phone, email, specialization, staff_number) VALUES
 ('Fatmata Conteh',  'Female', '+232 76 100200', 'f.conteh@example.org', 'Paediatrics',      'DOC-001'),
 ('Ibrahim Koroma',  'Male',   '+232 77 300400', 'i.koroma@example.org', 'General Practice', 'DOC-002'),
 ('Hawa Bangura',    'Female', '+232 78 500600', '',                     'Internal Medicine','DOC-003')
ON CONFLICT (staff_number) DO NOTHING;

INSERT INTO patients (full_name, gender, date_of_birth, phone, email, address, blood_group) VALUES
 ('Aminata Kamara',  'Female', '1995-04-12', '+232 76 123456', '',                 'Wilberforce, Freetown', 'O+'),
 ('Mohamed Sesay',   'Male',   '1988-11-03', '+232 79 654321', 'm.sesay@example.org','Bo Town',            'A+'),
 ('Isatu Jalloh',    'Female', '2016-07-21', '+232 88 222333', '',                 'Makeni',               'B-'),
 ('Alhaji Turay',    'Male',   '1960-01-30', '+232 30 444555', '',                 'Kenema',               'Unknown');

INSERT INTO appointments (patient_id, doctor_id, scheduled_at, reason, status) VALUES
 (1, 2, CURRENT_DATE + TIME '09:00' + INTERVAL '1 day', 'Follow-up check',      'Scheduled'),
 (3, 1, CURRENT_DATE + TIME '10:30' + INTERVAL '2 day', 'Routine immunisation', 'Scheduled'),
 (4, 3, CURRENT_DATE + TIME '14:00' - INTERVAL '3 day', 'Blood pressure review','Completed')
ON CONFLICT DO NOTHING;

INSERT INTO medical_records (patient_id, doctor_id, visit_date, diagnosis, treatment, notes) VALUES
 (1, 2, CURRENT_DATE - 10, 'Malaria (uncomplicated)', 'ACT course, 3 days', 'Return if fever persists'),
 (4, 3, CURRENT_DATE - 3,  'Hypertension',            'Amlodipine 5mg daily','Review in 1 month'),
 (3, 1, CURRENT_DATE - 30, 'Upper respiratory infection','Rest and fluids', '');
