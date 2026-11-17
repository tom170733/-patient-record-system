"""Console demo of the OOP concepts (no database or GUI needed).

    python demo_console.py

Useful for the presentation and for the report's "sample input/output".
"""
from datetime import datetime, timedelta

from manager import RecordManager
from models import Appointment, Doctor, Entity, MedicalRecord, Patient, Person


def heading(text):
    print(f"\n=== {text} ===")


heading("1. Creating objects (classes & objects)")
p1 = Patient("aminata kamara", "Female", "+232 76 123456", "1995-04-12", "O+",
             "Freetown", patient_id=1)
p2 = Patient("mohamed sesay", "Male", "+232 79 654321", "1988-11-03", "A+", "Bo", patient_id=2)
doc = Doctor("fatmata conteh", "Female", "+232 76 100200", "Paediatrics", "doc-001",
             doctor_id=1)
print(p1)
print(doc)

heading("2. Encapsulation (@property with validation)")
print("Age is calculated, not stored:", p1.age)
try:
    p1.phone = "abc"
except ValueError as err:
    print("Rejected bad phone ->", err)
try:
    p1.blood_group = "Z+"
except ValueError as err:
    print("Rejected bad blood group ->", err)

heading("3. Inheritance")
print("Patient MRO:", " -> ".join(c.__name__ for c in Patient.__mro__))
print("Doctor MRO (multiple):", " -> ".join(c.__name__ for c in Doctor.__mro__))
print("Doctor gets staff_badge() from StaffMixin:", doc.staff_badge())

heading("4. Abstract base class")
try:
    Person("x y", "Male", "0761234567")
except TypeError as err:
    print("Cannot create a Person directly ->", err)

heading("5. Polymorphism - one loop, different summary() methods")
appt = Appointment(1, 1, datetime.now() + timedelta(days=1), "Follow-up", appointment_id=1)
rec = MedicalRecord(1, 1, "2026-11-01", "Malaria", "ACT course", record_id=1)
for item in (p1, doc, appt, rec):
    print(f"{type(item).__name__:<14}", item.summary())

heading("6. Data structures - RecordManager (dict of objects)")
patients = RecordManager("Patient")
patients.add(p1)
patients.add(p2)
print("All:", patients.display())
print("Search 'sesay':", [p.full_name for p in patients.search("sesay")])
patients.delete(2)
print("After delete, count =", len(patients))

heading("7. Class & static methods")
print("Patients created:", Patient.objects_created())
print("Static check, valid phone '076 12':", Person.is_valid_phone("076 12"))
print("Alternative constructor:", Patient.from_dict(p2.to_dict() | {"patient_id": 9}))
print("Entity is abstract:", Entity.__abstractmethods__)
