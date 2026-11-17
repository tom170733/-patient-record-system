"""Patient - single inheritance from Person."""
from datetime import date

from .person import Person

BLOOD_GROUPS = ("A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "Unknown")


class Patient(Person):
    def __init__(self, full_name, gender, phone, date_of_birth,
                 blood_group="Unknown", address="", email="", patient_id=None):
        # super() passes the shared fields up to Person -> Entity.
        super().__init__(full_name=full_name, gender=gender, phone=phone,
                         email=email, entity_id=patient_id)
        self.__date_of_birth = None
        self.__blood_group = "Unknown"
        self.date_of_birth = date_of_birth
        self.blood_group = blood_group
        self.address = (address or "").strip()

    @property
    def date_of_birth(self):
        return self.__date_of_birth

    @date_of_birth.setter
    def date_of_birth(self, value):
        if isinstance(value, str):
            value = date.fromisoformat(value)
        if not isinstance(value, date) or value > date.today():
            raise ValueError("Date of birth must be a date that is not in the future.")
        self.__date_of_birth = value

    @property
    def blood_group(self):
        return self.__blood_group

    @blood_group.setter
    def blood_group(self, value):
        if value not in BLOOD_GROUPS:
            raise ValueError(f"Blood group must be one of {BLOOD_GROUPS}.")
        self.__blood_group = value

    @property
    def age(self):
        """Read-only property: calculated, never stored."""
        return Patient.calculate_age(self.date_of_birth)

    @staticmethod
    def calculate_age(dob, today=None):
        today = today or date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    @property
    def role(self):
        return "Patient"

    # Method overriding + super(): extend the parent's summary.
    def summary(self):
        return f"{super().summary()} | Age {self.age}, Blood {self.blood_group}"

    def to_dict(self):
        return {
            "full_name": self.full_name, "gender": self.gender,
            "date_of_birth": self.date_of_birth, "phone": self.phone,
            "email": self.email, "address": self.address,
            "blood_group": self.blood_group,
        }

    @classmethod
    def from_dict(cls, data):
        """Alternative constructor (class method) used by the database layer."""
        return cls(full_name=data["full_name"], gender=data["gender"],
                   phone=data["phone"], date_of_birth=data["date_of_birth"],
                   blood_group=data.get("blood_group", "Unknown"),
                   address=data.get("address") or "", email=data.get("email") or "",
                   patient_id=data.get("patient_id"))
