"""Person (abstract) and the StaffMixin used for multiple inheritance."""
import re
from abc import abstractmethod

from .entity import Entity

# Tuples hold fixed values that must never change (immutable) -> extra credit.
GENDERS = ("Male", "Female", "Other")


class Person(Entity):
    """Abstract parent of Patient and Doctor (hierarchical inheritance)."""

    def __init__(self, full_name, gender, phone, email="", **kwargs):
        super().__init__(**kwargs)
        # Double underscore = name-mangled "private" attributes.
        self.__full_name = ""
        self.__gender = ""
        self.__phone = ""
        self.__email = ""
        # Assigning through the setters runs the validation rules.
        self.full_name = full_name
        self.gender = gender
        self.phone = phone
        self.email = email

    # ---------- getters / setters with @property ----------
    @property
    def full_name(self):
        return self.__full_name

    @full_name.setter
    def full_name(self, value):
        value = (value or "").strip()
        if len(value) < 2:
            raise ValueError("Full name must have at least 2 characters.")
        self.__full_name = value.title()

    @property
    def gender(self):
        return self.__gender

    @gender.setter
    def gender(self, value):
        if value not in GENDERS:
            raise ValueError(f"Gender must be one of {GENDERS}.")
        self.__gender = value

    @property
    def phone(self):
        return self.__phone

    @phone.setter
    def phone(self, value):
        value = (value or "").strip()
        if not Person.is_valid_phone(value):
            raise ValueError("Phone must contain 7-15 digits (e.g. +232 76 123456).")
        self.__phone = value

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, value):
        value = (value or "").strip()
        if value and not Person.is_valid_email(value):
            raise ValueError("Email address is not valid.")
        self.__email = value

    # ---------- static methods (utility, no self/cls needed) ----------
    @staticmethod
    def is_valid_phone(phone):
        digits = re.sub(r"[\s\-+()]", "", phone or "")
        return digits.isdigit() and 7 <= len(digits) <= 15

    @staticmethod
    def is_valid_email(email):
        return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email or "") is not None

    # ---------- abstract part of the interface ----------
    @property
    @abstractmethod
    def role(self):
        """'Patient' or 'Doctor' - each subclass answers differently."""

    def validate(self):
        # The setters already validate; re-running them keeps the rule in one place.
        self.full_name, self.gender, self.phone, self.email = (
            self.full_name, self.gender, self.phone, self.email)

    def summary(self):
        return f"[{self.role}] {self.full_name} ({self.gender}) - {self.phone}"


class StaffMixin:
    """Adds hospital-staff behaviour. Combined with Person in Doctor
    to demonstrate MULTIPLE inheritance."""

    def __init__(self, staff_number="", **kwargs):
        super().__init__(**kwargs)
        self._staff_number = ""
        self.staff_number = staff_number

    @property
    def staff_number(self):
        return self._staff_number

    @staff_number.setter
    def staff_number(self, value):
        value = (value or "").strip().upper()
        if not re.fullmatch(r"[A-Z]{2,4}-\d{3,6}", value):
            raise ValueError("Staff number must look like DOC-001.")
        self._staff_number = value

    def staff_badge(self):
        return f"Staff {self.staff_number}"
