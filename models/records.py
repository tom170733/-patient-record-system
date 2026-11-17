"""Appointment and MedicalRecord - also subclasses of the abstract Entity,
so they share the same interface (validate / to_dict / summary)."""
from datetime import date, datetime

from .entity import Entity

APPOINTMENT_STATUSES = ("Scheduled", "Completed", "Cancelled")


class Appointment(Entity):
    def __init__(self, patient_id, doctor_id, scheduled_at, reason="",
                 status="Scheduled", appointment_id=None):
        super().__init__(entity_id=appointment_id)
        self.patient_id = int(patient_id)
        self.doctor_id = int(doctor_id)
        if isinstance(scheduled_at, str):
            scheduled_at = datetime.fromisoformat(scheduled_at)
        self.__scheduled_at = scheduled_at
        self.reason = (reason or "").strip()
        self.__status = "Scheduled"
        self.status = status
        # Filled in by the database layer for display only.
        self.patient_name = ""
        self.doctor_name = ""

    @property
    def scheduled_at(self):
        return self.__scheduled_at

    @scheduled_at.setter
    def scheduled_at(self, value):
        if not isinstance(value, datetime):
            raise ValueError("Appointment time must be a date and time.")
        self.__scheduled_at = value

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if value not in APPOINTMENT_STATUSES:
            raise ValueError(f"Status must be one of {APPOINTMENT_STATUSES}.")
        self.__status = value

    def cancel(self):
        if self.status == "Completed":
            raise ValueError("A completed appointment cannot be cancelled.")
        self.status = "Cancelled"

    def complete(self):
        self.status = "Completed"

    def validate(self):
        if not self.reason:
            raise ValueError("Please enter the reason for the appointment.")
        self.scheduled_at = self.scheduled_at

    def summary(self):
        who = self.patient_name or f"patient #{self.patient_id}"
        return f"Appointment {self.scheduled_at:%Y-%m-%d %H:%M} for {who} [{self.status}]"

    def to_dict(self):
        return {"patient_id": self.patient_id, "doctor_id": self.doctor_id,
                "scheduled_at": self.scheduled_at, "reason": self.reason,
                "status": self.status}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["patient_id"], data["doctor_id"], data["scheduled_at"],
                  data.get("reason", ""), data.get("status", "Scheduled"),
                  data.get("appointment_id"))
        obj.patient_name = data.get("patient_name", "")
        obj.doctor_name = data.get("doctor_name", "")
        return obj


class MedicalRecord(Entity):
    def __init__(self, patient_id, doctor_id, visit_date, diagnosis,
                 treatment="", notes="", record_id=None):
        super().__init__(entity_id=record_id)
        self.patient_id = int(patient_id)
        self.doctor_id = int(doctor_id)
        if isinstance(visit_date, str):
            visit_date = date.fromisoformat(visit_date)
        self.visit_date = visit_date
        self.__diagnosis = ""
        self.diagnosis = diagnosis
        self.treatment = (treatment or "").strip()
        self.notes = (notes or "").strip()
        self.patient_name = ""
        self.doctor_name = ""

    @property
    def diagnosis(self):
        return self.__diagnosis

    @diagnosis.setter
    def diagnosis(self, value):
        value = (value or "").strip()
        if not value:
            raise ValueError("Diagnosis is required.")
        self.__diagnosis = value

    def validate(self):
        self.diagnosis = self.diagnosis
        if self.visit_date > date.today():
            raise ValueError("Visit date cannot be in the future.")

    def summary(self):
        who = self.patient_name or f"patient #{self.patient_id}"
        return f"Record {self.visit_date:%Y-%m-%d}: {who} - {self.diagnosis}"

    def to_dict(self):
        return {"patient_id": self.patient_id, "doctor_id": self.doctor_id,
                "visit_date": self.visit_date, "diagnosis": self.diagnosis,
                "treatment": self.treatment, "notes": self.notes}

    @classmethod
    def from_dict(cls, data):
        obj = cls(data["patient_id"], data["doctor_id"], data["visit_date"],
                  data["diagnosis"], data.get("treatment", ""), data.get("notes", ""),
                  data.get("record_id"))
        obj.patient_name = data.get("patient_name", "")
        obj.doctor_name = data.get("doctor_name", "")
        return obj
