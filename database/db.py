"""PostgreSQL access with psycopg2 (Task 7).

Database      - opens the connection and runs schema.sql.
Repository    - abstract base: generic add / update / delete / get_all.
Concrete repositories only say which table they use and how to turn a
row into an object -> inheritance + polymorphism in the data layer too.
"""
import os
from abc import ABC, abstractmethod
from pathlib import Path

import psycopg2
import psycopg2.extras
from psycopg2 import sql

from models import Appointment, Doctor, MedicalRecord, Patient

SCHEMA_FILE = Path(__file__).with_name("schema.sql")


class DatabaseError(Exception):
    """Friendly error the GUI can show to the user."""


class Database:
    def __init__(self, **settings):
        # Settings come from environment variables so passwords are never in the code.
        self._settings = {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432"),
            "dbname": os.getenv("DB_NAME", "patient_records"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),
        }
        self._settings.update(settings)
        self._conn = None

    def connect(self):
        try:
            self._conn = psycopg2.connect(**self._settings)
        except psycopg2.OperationalError as exc:
            raise DatabaseError(
                f"Could not connect to PostgreSQL database "
                f"'{self._settings['dbname']}' on {self._settings['host']}.\n\n{exc}") from exc
        return self

    def create_schema(self):
        self.execute(SCHEMA_FILE.read_text(encoding="utf-8"))

    def execute(self, query, params=None, fetch=None):
        """Run a query inside a transaction. fetch = None | 'one' | 'all'."""
        if self._conn is None:
            self.connect()
        try:
            with self._conn:  # commits on success, rolls back on error
                with self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                    cur.execute(query, params)
                    if fetch == "one":
                        return cur.fetchone()
                    if fetch == "all":
                        return cur.fetchall()
                    return None
        except psycopg2.errors.UniqueViolation as exc:
            messages = {
                "uq_doctor_slot": "This doctor already has an appointment at that time.",
                "doctors_staff_number_key": "Another doctor already uses that staff number.",
            }
            raise DatabaseError(messages.get(exc.diag.constraint_name,
                                             "This record already exists (duplicate value).")) from exc
        except psycopg2.errors.ForeignKeyViolation as exc:
            raise DatabaseError("This item is still used by other records "
                                "(e.g. a doctor with appointments) and cannot be deleted.") from exc
        except psycopg2.errors.CheckViolation as exc:
            raise DatabaseError(f"The database rejected an invalid value.\n{exc.diag.message_primary}") from exc
        except psycopg2.Error as exc:
            raise DatabaseError(str(exc)) from exc

    def close(self):
        if self._conn is not None:
            self._conn.close()
            self._conn = None


class Repository(ABC):
    table = ""          # table to write to
    view = ""           # table or view to read from
    id_column = ""

    def __init__(self, db):
        self.db = db

    @abstractmethod
    def from_row(self, row):
        """Turn a database row (dict) into a model object."""

    def add(self, obj):
        obj.validate()
        data = obj.to_dict()
        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING {}").format(
            sql.Identifier(self.table),
            sql.SQL(", ").join(map(sql.Identifier, data)),
            sql.SQL(", ").join(sql.Placeholder() * len(data)),
            sql.Identifier(self.id_column))
        row = self.db.execute(query, list(data.values()), fetch="one")
        obj.id = row[self.id_column]
        return obj

    def update(self, obj):
        obj.validate()
        data = obj.to_dict()
        query = sql.SQL("UPDATE {} SET {} WHERE {} = %s").format(
            sql.Identifier(self.table),
            sql.SQL(", ").join(sql.SQL("{} = %s").format(sql.Identifier(k)) for k in data),
            sql.Identifier(self.id_column))
        self.db.execute(query, list(data.values()) + [obj.id])
        return obj

    def delete(self, obj_id):
        query = sql.SQL("DELETE FROM {} WHERE {} = %s").format(
            sql.Identifier(self.table), sql.Identifier(self.id_column))
        self.db.execute(query, [obj_id])

    def get_all(self):
        query = sql.SQL("SELECT * FROM {} ORDER BY {}").format(
            sql.Identifier(self.view or self.table), sql.Identifier(self.id_column))
        return [self.from_row(r) for r in self.db.execute(query, fetch="all")]


class PatientRepository(Repository):
    table, id_column = "patients", "patient_id"

    def from_row(self, row):
        return Patient.from_dict(row)


class DoctorRepository(Repository):
    table, id_column = "doctors", "doctor_id"

    def from_row(self, row):
        return Doctor.from_dict(row)


class AppointmentRepository(Repository):
    table, view, id_column = "appointments", "v_appointments", "appointment_id"

    def from_row(self, row):
        return Appointment.from_dict(row)


class MedicalRecordRepository(Repository):
    table, view, id_column = "medical_records", "v_medical_records", "record_id"

    def from_row(self, row):
        return MedicalRecord.from_dict(row)
