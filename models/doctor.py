"""Doctor - MULTIPLE inheritance from Person and StaffMixin."""
from .person import Person, StaffMixin

SPECIALIZATIONS = ("General Practice", "Paediatrics", "Obstetrics & Gynaecology",
                   "Internal Medicine", "Surgery", "Cardiology", "Dermatology",
                   "Psychiatry", "Other")


class Doctor(Person, StaffMixin):
    """Method Resolution Order: Doctor -> Person -> Entity -> StaffMixin.
    Each __init__ calls super().__init__(**kwargs) so every parent runs once."""

    def __init__(self, full_name, gender, phone, specialization, staff_number,
                 email="", doctor_id=None):
        super().__init__(full_name=full_name, gender=gender, phone=phone,
                         email=email, staff_number=staff_number, entity_id=doctor_id)
        self.__specialization = ""
        self.specialization = specialization

    @property
    def specialization(self):
        return self.__specialization

    @specialization.setter
    def specialization(self, value):
        if value not in SPECIALIZATIONS:
            raise ValueError(f"Specialization must be one of {SPECIALIZATIONS}.")
        self.__specialization = value

    @property
    def role(self):
        return "Doctor"

    def summary(self):
        return f"Dr. {self.full_name} - {self.specialization} ({self.staff_badge()})"

    def validate(self):
        super().validate()
        self.staff_number = self.staff_number

    def to_dict(self):
        return {
            "full_name": self.full_name, "gender": self.gender, "phone": self.phone,
            "email": self.email, "specialization": self.specialization,
            "staff_number": self.staff_number,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(full_name=data["full_name"], gender=data["gender"],
                   phone=data["phone"], specialization=data["specialization"],
                   staff_number=data["staff_number"], email=data.get("email") or "",
                   doctor_id=data.get("doctor_id"))
