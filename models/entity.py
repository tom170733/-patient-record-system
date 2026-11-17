"""Abstract base class shared by every domain object.

OOP concepts shown here:
  * Abstract base class (ABC) with abstract methods  -> Task 6 (interfaces)
  * Encapsulation: a "private" attribute exposed through @property -> Task 4
  * Class methods and a class-level counter             -> Task 2
"""
from abc import ABC, abstractmethod


class Entity(ABC):
    """Anything that is stored in the database and has an ID."""

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._created = 0  # each subclass gets its own object counter

    def __init__(self, entity_id=None, **kwargs):
        # **kwargs keeps the constructor chain cooperative, which is what
        # makes multiple inheritance (see Doctor) work with super().
        super().__init__(**kwargs)
        self._id = None
        self.id = entity_id
        type(self)._created += 1

    # ---------- encapsulated ID ----------
    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if value is not None and int(value) <= 0:
            raise ValueError("ID must be a positive number.")
        self._id = int(value) if value is not None else None

    # ---------- class method ----------
    @classmethod
    def objects_created(cls):
        """How many objects of this class have been created this session."""
        return cls._created

    # ---------- the "interface" every subclass must implement ----------
    @abstractmethod
    def validate(self):
        """Raise ValueError if the object holds invalid data."""

    @abstractmethod
    def to_dict(self):
        """Return the object's data as a dictionary (used by the database layer)."""

    @abstractmethod
    def summary(self):
        """Return a one-line, human-readable description (polymorphic)."""

    def __str__(self):
        return self.summary()

    def __repr__(self):
        return f"{type(self).__name__}(id={self._id})"
