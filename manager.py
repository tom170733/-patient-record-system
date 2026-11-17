"""In-memory data structure for managing many objects (Task 3).

A dictionary keyed by ID gives fast lookup, update and delete.
The GUI keeps one RecordManager per tab as a cache of what is in PostgreSQL.
"""


class RecordManager:
    def __init__(self, label):
        self.label = label
        self._items = {}          # dict: {id: Entity}

    def add(self, item):
        if item.id is None:
            raise ValueError("Save the item to the database first so it has an ID.")
        if item.id in self._items:
            raise KeyError(f"{self.label} #{item.id} already exists.")
        self._items[item.id] = item

    def update(self, item):
        if item.id not in self._items:
            raise KeyError(f"{self.label} #{item.id} not found.")
        self._items[item.id] = item

    def delete(self, item_id):
        return self._items.pop(item_id)

    def get(self, item_id):
        return self._items.get(item_id)

    def replace_all(self, items):
        self._items = {item.id: item for item in items}

    def all(self):
        return list(self._items.values())     # list for ordered display

    def search(self, text):
        text = (text or "").lower().strip()
        return [i for i in self._items.values() if text in i.summary().lower()]

    def display(self):
        """Polymorphism: summary() runs the right version for each class."""
        return [item.summary() for item in self._items.values()]

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items.values())
