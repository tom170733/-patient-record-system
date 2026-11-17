"""The four screens. Each overrides the BaseCrudTab hooks (polymorphism)."""
from datetime import datetime

from PyQt6.QtCore import QDate, QDateTime, QTime
from PyQt6.QtWidgets import QDateEdit, QDateTimeEdit, QLineEdit, QPlainTextEdit

from models import (APPOINTMENT_STATUSES, BLOOD_GROUPS, GENDERS, SPECIALIZATIONS,
                    Appointment, Doctor, MedicalRecord, Patient)

from .base_tab import BaseCrudTab, PeopleChoicesMixin


def _date_edit(maximum_today=True):
    d = QDateEdit(calendarPopup=True)
    d.setDisplayFormat("yyyy-MM-dd")
    if maximum_today:
        d.setMaximumDate(QDate.currentDate())
    d.setDate(QDate.currentDate())
    return d


class PatientsTab(BaseCrudTab):
    title = "Patient"
    headers = ("ID", "Full name", "Gender", "Date of birth", "Age", "Phone", "Blood group")

    def build_form(self, form):
        self.name = self.add_field(form, "Full &name *", QLineEdit(), "Patient's full name")
        self.gender = self.add_field(form, "&Gender *", self.combo(GENDERS))
        self.dob = self.add_field(form, "Date of &birth *", _date_edit(), "Format: YYYY-MM-DD")
        self.phone = self.add_field(form, "&Phone *", QLineEdit(), "7-15 digits, e.g. +232 76 123456")
        self.email = self.add_field(form, "&Email", QLineEdit(), "Optional")
        self.address = self.add_field(form, "Add&ress", QLineEdit(), "Town or street address")
        self.blood = self.add_field(form, "B&lood group", self.combo(BLOOD_GROUPS))

    def read_form(self):
        return Patient(self.name.text(), self.gender.currentText(), self.phone.text(),
                       self.dob.date().toPyDate(), self.blood.currentText(),
                       self.address.text(), self.email.text())

    def fill_form(self, p):
        self.name.setText(p.full_name)
        self.gender.setCurrentText(p.gender)
        self.dob.setDate(QDate(p.date_of_birth))
        self.phone.setText(p.phone)
        self.email.setText(p.email)
        self.address.setText(p.address)
        self.blood.setCurrentText(p.blood_group)

    def clear_form(self):
        for w in (self.name, self.phone, self.email, self.address):
            w.clear()
        self.gender.setCurrentIndex(0)
        self.blood.setCurrentText("Unknown")
        self.dob.setDate(QDate(2000, 1, 1))

    def row_values(self, p):
        return (p.id, p.full_name, p.gender, p.date_of_birth, p.age, p.phone, p.blood_group)


class DoctorsTab(BaseCrudTab):
    title = "Doctor"
    headers = ("ID", "Full name", "Specialization", "Staff no.", "Phone", "Email")

    def build_form(self, form):
        self.name = self.add_field(form, "Full &name *", QLineEdit(), "Doctor's full name")
        self.gender = self.add_field(form, "&Gender *", self.combo(GENDERS))
        self.phone = self.add_field(form, "&Phone *", QLineEdit(), "7-15 digits")
        self.email = self.add_field(form, "&Email", QLineEdit(), "Optional")
        self.spec = self.add_field(form, "Speciali&zation *", self.combo(SPECIALIZATIONS))
        self.staff = self.add_field(form, "S&taff number *", QLineEdit(), "Format: DOC-001")

    def read_form(self):
        return Doctor(self.name.text(), self.gender.currentText(), self.phone.text(),
                      self.spec.currentText(), self.staff.text(), self.email.text())

    def fill_form(self, d):
        self.name.setText(d.full_name)
        self.gender.setCurrentText(d.gender)
        self.phone.setText(d.phone)
        self.email.setText(d.email)
        self.spec.setCurrentText(d.specialization)
        self.staff.setText(d.staff_number)

    def clear_form(self):
        for w in (self.name, self.phone, self.email, self.staff):
            w.clear()
        self.gender.setCurrentIndex(0)
        self.spec.setCurrentIndex(0)

    def row_values(self, d):
        return (d.id, d.full_name, d.specialization, d.staff_number, d.phone, d.email)


class AppointmentsTab(PeopleChoicesMixin, BaseCrudTab):
    title = "Appointment"
    headers = ("ID", "Date & time", "Patient", "Doctor", "Reason", "Status")

    def __init__(self, repository, patient_repo, doctor_repo, parent=None):
        self.patient_repo, self.doctor_repo = patient_repo, doctor_repo
        super().__init__(repository, parent)

    def build_form(self, form):
        self.patient = self.add_field(form, "&Patient *", self.combo([]))
        self.doctor = self.add_field(form, "&Doctor *", self.combo([]))
        self.when = QDateTimeEdit(calendarPopup=True)
        self.when.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.add_field(form, "Date && &time *", self.when, "When the appointment starts")
        self.reason = self.add_field(form, "&Reason *", QLineEdit(), "e.g. Follow-up check")
        self.status = self.add_field(form, "&Status", self.combo(APPOINTMENT_STATUSES))

    def refresh_choices(self):
        self.fill_people_combos(self.patient, self.doctor, self.patient_repo, self.doctor_repo)

    def read_form(self):
        if self.patient.currentData() is None or self.doctor.currentData() is None:
            raise ValueError("Add a patient and a doctor first, then choose them here.")
        return Appointment(self.patient.currentData(), self.doctor.currentData(),
                           self.when.dateTime().toPyDateTime().replace(second=0, microsecond=0),
                           self.reason.text(), self.status.currentText())

    def fill_form(self, a):
        self.select_data(self.patient, a.patient_id)
        self.select_data(self.doctor, a.doctor_id)
        self.when.setDateTime(QDateTime(a.scheduled_at))
        self.reason.setText(a.reason)
        self.status.setCurrentText(a.status)

    def clear_form(self):
        tomorrow = QDateTime(QDate.currentDate().addDays(1), QTime(9, 0))
        self.when.setDateTime(tomorrow)
        self.reason.clear()
        self.status.setCurrentIndex(0)

    def row_values(self, a):
        return (a.id, f"{a.scheduled_at:%Y-%m-%d %H:%M}", a.patient_name,
                f"Dr. {a.doctor_name}", a.reason, a.status)


class RecordsTab(PeopleChoicesMixin, BaseCrudTab):
    title = "Medical record"
    headers = ("ID", "Visit date", "Patient", "Doctor", "Diagnosis", "Treatment")

    def __init__(self, repository, patient_repo, doctor_repo, parent=None):
        self.patient_repo, self.doctor_repo = patient_repo, doctor_repo
        super().__init__(repository, parent)

    def build_form(self, form):
        self.patient = self.add_field(form, "&Patient *", self.combo([]))
        self.doctor = self.add_field(form, "&Doctor *", self.combo([]))
        self.visit = self.add_field(form, "&Visit date *", _date_edit())
        self.diagnosis = self.add_field(form, "Dia&gnosis *", QLineEdit())
        self.treatment = QPlainTextEdit()
        self.treatment.setFixedHeight(70)
        self.add_field(form, "&Treatment", self.treatment, "Medicines or procedures given")
        self.notes = QPlainTextEdit()
        self.notes.setFixedHeight(70)
        self.add_field(form, "N&otes", self.notes, "Any other information")
        self.notes.setTabChangesFocus(True)
        self.treatment.setTabChangesFocus(True)

    def refresh_choices(self):
        self.fill_people_combos(self.patient, self.doctor, self.patient_repo, self.doctor_repo)

    def read_form(self):
        if self.patient.currentData() is None or self.doctor.currentData() is None:
            raise ValueError("Add a patient and a doctor first, then choose them here.")
        return MedicalRecord(self.patient.currentData(), self.doctor.currentData(),
                             self.visit.date().toPyDate(), self.diagnosis.text(),
                             self.treatment.toPlainText(), self.notes.toPlainText())

    def fill_form(self, r):
        self.select_data(self.patient, r.patient_id)
        self.select_data(self.doctor, r.doctor_id)
        self.visit.setDate(QDate(r.visit_date))
        self.diagnosis.setText(r.diagnosis)
        self.treatment.setPlainText(r.treatment)
        self.notes.setPlainText(r.notes)

    def clear_form(self):
        self.visit.setDate(QDate.currentDate())
        self.diagnosis.clear()
        self.treatment.clear()
        self.notes.clear()

    def row_values(self, r):
        return (r.id, r.visit_date, r.patient_name, f"Dr. {r.doctor_name}",
                r.diagnosis, r.treatment)
