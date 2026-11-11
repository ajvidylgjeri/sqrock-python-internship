# Hospital Management System (Flask + SQLite)

Sqrock IT Solutions Python Internship — Phase 1, Task 2.

A web application to manage hospital operations. Runs fully offline — the SQLite database is created and seeded automatically on first run.

## Features
- **Dashboard** with live counts (patients, doctors, appointments) and paid revenue
- **Patient registration** with search by name/ailment and delete
- **Doctor management** (add, list, specialty, fee)
- **Appointment booking** linking patients to doctors, with mark-as-completed
- **Billing** — create bills, mark paid, revenue reflected on the dashboard
- Sidebar navigation, flash messages, responsive layout

## Run
```bash
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5000
```
The database file `hospital.db` is created automatically (and seeded with sample doctors/patients) on first launch.

## Tech
Python · Flask · Jinja2 templates · SQLite (`sqlite3`) · HTML/CSS.

**Author:** Ajvi Dylgjeri
