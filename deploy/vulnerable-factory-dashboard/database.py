import sqlite3

DATABASE = "factory.db"

HANDOVER_SCHEMA = """
CREATE TABLE IF NOT EXISTS handover_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shift_date TEXT NOT NULL,
    work_order TEXT NOT NULL,
    furnace_1 TEXT NOT NULL,
    furnace_2 TEXT NOT NULL,
    furnace_3 TEXT NOT NULL,
    furnace_4 TEXT NOT NULL,
    accidents TEXT NOT NULL,
    attendance INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
"""

SCHEMA = """
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS grievances;
DROP TABLE IF EXISTS handover_notes;
DROP TABLE IF EXISTS vault_keys;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'employee',
    department TEXT,
    performance_score INTEGER DEFAULT 0,
    employee_id_number TEXT,
    salary INTEGER,
    secret_note TEXT
);

CREATE TABLE grievances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE vault_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key_name TEXT NOT NULL,
    key_value TEXT NOT NULL
);
""" + HANDOVER_SCHEMA

# username, password, full_name, role, department, performance_score,
# employee_id_number, salary, secret_note
EMPLOYEES = [
    ("geligah", "summer2024", "Geoff Eligah", "employee", "Production", 92, "EMP-1042", 48000, None),
    ("bnatas", "letmein", "Benjamin Natas", "employee", "Quality Control", 88, "EMP-1077", 51000, None),
    ("jdeeler", "jmehta2023", "John Deeler", "employee", "Maintenance", 95, "EMP-1013", 53000, None),
    ("adas", "password123", "Sourav Das", "employee", "Logistics", 74, "EMP-1098", 46000, None),
    ("ckirk", "heIsalive", "Charlie Kirk", "employee", "HR", 68, "EMP-1061", 49500, None),
    ("vjoseph", "pm2029", "Vijay Joseph", "employee", "CM", 81, "EMP-1055", 47000, None),
    ("kgowda", "kgowda321", "Kiran Gowda", "employee", "Quality Control", 90, "EMP-1029", 50500, None),
    (
        "admin",
        "admin123",
        "Factory Admin",
        "admin",
        "Management",
        0,
        "EMP-0001",
        0,
        "AxA{1d0r_3xpos3d_th3_adm1n_n0t3_002}",
    ),
]

# key_name, key_value  (employee-search UNION injection target)
VAULT_KEYS = [
    ("furnace-ctl-panel", "KEY-8841-F2C1"),
    ("ops-master", "AxA{un10n_s3l3ct_dr41ns_th3_v4ult_001}"),
    ("cctv-archive", "KEY-2207-C9A4"),
]

# user_id (position in EMPLOYEES above, 1-indexed), subject, message, status
GRIEVANCES = [
    (1, "Overtime not compensated", "I worked 6 extra hours last week and it hasn't shown up in payroll.", "Pending"),
    (2, "Broken ventilation on floor 2", "The exhaust fan near QC station 3 has been off for two weeks.", "In Review"),
    (3, "Request for new safety gloves", "Current batch is worn through, need replacements for the whole shift.", "Pending"),
    (4, "Shift swap request", "Asked to swap with Tara for next Friday, no response yet.", "Pending"),
    (
        8,
        "Confidential: leadership review notes",
        "AxA{gr13vance_idor_l3aks_c0nf1dential_notes_003} -- do not forward outside management.",
        "Pending",
    ),
]

# user_id, shift_date, work_order, furnace 1-4 status, accidents, attendance
HANDOVER_NOTES = [
    (3, "2026-10-01", "WO-4410: Smelt 120 ancient debris into netherite scrap", "Running", "Running", "Idle", "Under Maintenance", "No", 28),
    (1, "2026-10-02", "WO-4411: Alloy netherite scrap with gold, ingot batch B7", "Running", "Running", "Running", "Idle", "No", 29),
]


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.executescript(SCHEMA)
    conn.executemany(
        "INSERT INTO users (username, password, full_name, role, department, "
        "performance_score, employee_id_number, salary, secret_note) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        EMPLOYEES,
    )
    conn.executemany(
        "INSERT INTO vault_keys (key_name, key_value) VALUES (?, ?)",
        VAULT_KEYS,
    )
    conn.executemany(
        "INSERT INTO grievances (user_id, subject, message, status) VALUES (?, ?, ?, ?)",
        GRIEVANCES,
    )
    conn.executemany(
        "INSERT INTO handover_notes (user_id, shift_date, work_order, furnace_1, furnace_2, "
        "furnace_3, furnace_4, accidents, attendance) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        HANDOVER_NOTES,
    )
    conn.commit()
    conn.close()
    print(f"Initialized {DATABASE} with {len(EMPLOYEES)} users and {len(GRIEVANCES)} grievances.")


if __name__ == "__main__":
    init_db()
