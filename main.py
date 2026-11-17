"""Start the Patient Record System.

    python main.py

Database settings are read from environment variables (see .env.example).
"""
import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMessageBox

from database import Database, DatabaseError
from gui import MainWindow


def load_env_file(path=".env"):
    """Tiny .env reader so no extra package is needed."""
    import os
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
    except FileNotFoundError:
        pass


def main():
    load_env_file()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont(app.font().family(), 11))   # larger default text for readability

    db = Database()
    try:
        db.connect()
        db.create_schema()          # creates tables on first run
    except DatabaseError as exc:
        QMessageBox.critical(None, "Database connection failed",
                             f"{exc}\n\nCheck that PostgreSQL is running and the "
                             "settings in your .env file are correct.")
        return 1

    window = MainWindow(db)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
