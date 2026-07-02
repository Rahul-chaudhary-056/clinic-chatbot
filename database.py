import sqlite3
from datetime import datetime

DB_NAME = "clinic.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            patient_phone TEXT,
            date TEXT,
            time_slot TEXT,
            status TEXT DEFAULT 'confirmed',
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def get_available_slots(date):
    """Returns list of slots not yet booked for a given date."""
    all_slots = ["10:00 AM", "11:00 AM", "12:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"]
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT time_slot FROM appointments WHERE date = ? AND status = 'confirmed'", (date,))
    booked = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return [slot for slot in all_slots if slot not in booked]

def book_appointment(patient_phone, date, time_slot, patient_name="Patient"):
    """Books a slot if available. Returns True if successful, False if already taken."""
    available = get_available_slots(date)
    if time_slot not in available:
        return False

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_name, patient_phone, date, time_slot, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (patient_name, patient_phone, date, time_slot, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True

def get_patient_appointments(patient_phone):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT date, time_slot FROM appointments WHERE patient_phone = ? AND status = 'confirmed'", (patient_phone,))
    results = cursor.fetchall()
    conn.close()
    return results

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully")