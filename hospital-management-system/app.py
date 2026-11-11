"""
Hospital Management System — Sqrock IT Solutions Python Internship (Phase 1, Task 2)

A Flask + SQLite web application to manage patients, doctors, appointments and
billing. Runs fully offline — the SQLite database is created and seeded
automatically on first run.

Run:
    pip install -r requirements.txt
    python app.py
    # open http://127.0.0.1:5000

Author: Ajvi Dylgjeri
"""
import os
import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, g, flash

app = Flask(__name__)
app.secret_key = "sqrock-hms-demo-key"
DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")


# --------------------------- database helpers ---------------------------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    first_time = not os.path.exists(DB_PATH)
    db = sqlite3.connect(DB_PATH)
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS patients(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, age INTEGER, gender TEXT,
            phone TEXT, ailment TEXT);
        CREATE TABLE IF NOT EXISTS doctors(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, specialty TEXT, phone TEXT, fee REAL);
        CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER, doctor_id INTEGER, date TEXT, status TEXT);
        CREATE TABLE IF NOT EXISTS bills(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER, description TEXT, amount REAL,
            paid INTEGER DEFAULT 0, date TEXT);
        """
    )
    if first_time:
        db.executemany("INSERT INTO doctors(name,specialty,phone,fee) VALUES(?,?,?,?)",
                       [("Dr. Elira Hoxha", "Cardiology", "069-100-1001", 50),
                        ("Dr. Marco Rossi", "Pediatrics", "069-100-1002", 35),
                        ("Dr. Ana Krasniqi", "Dermatology", "069-100-1003", 40)])
        db.executemany("INSERT INTO patients(name,age,gender,phone,ailment) VALUES(?,?,?,?,?)",
                       [("John Doe", 34, "Male", "069-200-2001", "Chest pain"),
                        ("Maria Leka", 28, "Female", "069-200-2002", "Skin rash")])
    db.commit()
    db.close()


# --------------------------- routes ---------------------------
@app.route("/")
def dashboard():
    db = get_db()
    stats = {
        "patients": db.execute("SELECT COUNT(*) c FROM patients").fetchone()["c"],
        "doctors": db.execute("SELECT COUNT(*) c FROM doctors").fetchone()["c"],
        "appointments": db.execute("SELECT COUNT(*) c FROM appointments").fetchone()["c"],
        "revenue": db.execute("SELECT COALESCE(SUM(amount),0) s FROM bills WHERE paid=1").fetchone()["s"],
    }
    upcoming = db.execute(
        """SELECT a.id, a.date, a.status, p.name patient, d.name doctor
           FROM appointments a JOIN patients p ON a.patient_id=p.id
           JOIN doctors d ON a.doctor_id=d.id ORDER BY a.date DESC LIMIT 5"""
    ).fetchall()
    return render_template("dashboard.html", stats=stats, upcoming=upcoming)


# ---- Patients ----
@app.route("/patients", methods=["GET", "POST"])
def patients():
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("INSERT INTO patients(name,age,gender,phone,ailment) VALUES(?,?,?,?,?)",
                   (f["name"], f.get("age") or None, f.get("gender"), f.get("phone"), f.get("ailment")))
        db.commit()
        flash("Patient registered successfully.")
        return redirect(url_for("patients"))
    q = request.args.get("q", "").strip()
    if q:
        rows = db.execute("SELECT * FROM patients WHERE name LIKE ? OR ailment LIKE ? ORDER BY id DESC",
                          (f"%{q}%", f"%{q}%")).fetchall()
    else:
        rows = db.execute("SELECT * FROM patients ORDER BY id DESC").fetchall()
    return render_template("patients.html", rows=rows, q=q)


@app.route("/patients/<int:pid>/delete", methods=["POST"])
def delete_patient(pid):
    db = get_db()
    db.execute("DELETE FROM patients WHERE id=?", (pid,))
    db.commit()
    flash("Patient removed.")
    return redirect(url_for("patients"))


# ---- Doctors ----
@app.route("/doctors", methods=["GET", "POST"])
def doctors():
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("INSERT INTO doctors(name,specialty,phone,fee) VALUES(?,?,?,?)",
                   (f["name"], f.get("specialty"), f.get("phone"), f.get("fee") or 0))
        db.commit()
        flash("Doctor added.")
        return redirect(url_for("doctors"))
    rows = db.execute("SELECT * FROM doctors ORDER BY id DESC").fetchall()
    return render_template("doctors.html", rows=rows)


# ---- Appointments ----
@app.route("/appointments", methods=["GET", "POST"])
def appointments():
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("INSERT INTO appointments(patient_id,doctor_id,date,status) VALUES(?,?,?,?)",
                   (f["patient_id"], f["doctor_id"], f.get("date") or str(date.today()), "Scheduled"))
        db.commit()
        flash("Appointment booked.")
        return redirect(url_for("appointments"))
    rows = db.execute(
        """SELECT a.id, a.date, a.status, p.name patient, d.name doctor
           FROM appointments a JOIN patients p ON a.patient_id=p.id
           JOIN doctors d ON a.doctor_id=d.id ORDER BY a.date DESC"""
    ).fetchall()
    patients_ = db.execute("SELECT id,name FROM patients ORDER BY name").fetchall()
    doctors_ = db.execute("SELECT id,name FROM doctors ORDER BY name").fetchall()
    return render_template("appointments.html", rows=rows, patients=patients_, doctors=doctors_,
                           today=str(date.today()))


@app.route("/appointments/<int:aid>/done", methods=["POST"])
def complete_appointment(aid):
    db = get_db()
    db.execute("UPDATE appointments SET status='Completed' WHERE id=?", (aid,))
    db.commit()
    return redirect(url_for("appointments"))


# ---- Billing ----
@app.route("/billing", methods=["GET", "POST"])
def billing():
    db = get_db()
    if request.method == "POST":
        f = request.form
        db.execute("INSERT INTO bills(patient_id,description,amount,paid,date) VALUES(?,?,?,?,?)",
                   (f["patient_id"], f.get("description"), f.get("amount") or 0,
                    1 if f.get("paid") else 0, str(date.today())))
        db.commit()
        flash("Bill created.")
        return redirect(url_for("billing"))
    rows = db.execute(
        """SELECT b.id, b.description, b.amount, b.paid, b.date, p.name patient
           FROM bills b JOIN patients p ON b.patient_id=p.id ORDER BY b.id DESC"""
    ).fetchall()
    patients_ = db.execute("SELECT id,name FROM patients ORDER BY name").fetchall()
    return render_template("billing.html", rows=rows, patients=patients_)


@app.route("/billing/<int:bid>/pay", methods=["POST"])
def pay_bill(bid):
    db = get_db()
    db.execute("UPDATE bills SET paid=1 WHERE id=?", (bid,))
    db.commit()
    flash("Bill marked as paid.")
    return redirect(url_for("billing"))


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
