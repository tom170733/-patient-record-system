import csv

from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QTabWidget

from database import (AppointmentRepository, DoctorRepository, MedicalRecordRepository,
                      PatientRepository)

from .tabs import AppointmentsTab, DoctorsTab, PatientsTab, RecordsTab

APP_NAME = "Patient Record System"
APP_VERSION = "1.0.0"


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle(APP_NAME)
        self.resize(1280, 640)

        patients, doctors = PatientRepository(db), DoctorRepository(db)
        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Sections")
        self.pages = [
            PatientsTab(patients),
            DoctorsTab(doctors),
            AppointmentsTab(AppointmentRepository(db), patients, doctors),
            RecordsTab(MedicalRecordRepository(db), patients, doctors),
        ]
        # Switch tabs with Ctrl+Tab / Ctrl+Shift+Tab (no Alt shortcuts, so they
        # don't clash with the form fields' Alt shortcuts).
        for page, label in zip(self.pages, ("Patients", "Doctors", "Appointments",
                                            "Medical Records")):
            self.tabs.addTab(page, label)
            page.status_message.connect(lambda msg: self.statusBar().showMessage(msg, 6000))
        self.tabs.currentChanged.connect(self.refresh_current)
        self.setCentralWidget(self.tabs)
        self._build_menu()
        self.refresh_current()
        self.statusBar().showMessage("Connected to PostgreSQL.", 4000)

    def _build_menu(self):
        file_menu = self.menuBar().addMenu("&File")
        refresh = QAction("&Refresh", self, shortcut=QKeySequence("F5"))
        refresh.triggered.connect(self.refresh_current)
        export = QAction("&Export this tab to CSV...", self, shortcut=QKeySequence("Ctrl+E"))
        export.triggered.connect(self.export_csv)
        quit_action = QAction("E&xit", self, shortcut=QKeySequence("Ctrl+Q"))
        quit_action.triggered.connect(self.close)
        file_menu.addActions([refresh, export, quit_action])

        help_menu = self.menuBar().addMenu("&Help")
        about = QAction("&About", self)
        about.triggered.connect(self.show_about)
        help_menu.addAction(about)

    def refresh_current(self, *_):
        page = self.tabs.currentWidget()
        page.refresh_choices()
        page.load()

    def export_csv(self):
        """DPG: data can be taken out in an open, non-proprietary format."""
        page = self.tabs.currentWidget()
        default = f"{page.title.lower().replace(' ', '_')}s.csv"
        path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", default, "CSV files (*.csv)")
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(page.headers)
            writer.writerows(page.row_values(obj) for obj in page.manager.all())
        self.statusBar().showMessage(f"Exported {len(page.manager)} rows to {path}", 6000)

    def show_about(self):
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> v{APP_VERSION}<br><br>"
            "Open-source patient records for small clinics.<br>"
            "Released under the MIT Licence as a Digital Public Good.<br><br>"
            "Keyboard: Ctrl+N add, Ctrl+S update, Del delete, Esc clear,<br>"
            "F5 refresh, Ctrl+E export CSV, Ctrl+Tab next section.")

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event)
