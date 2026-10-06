# 🏭 Blast Furnace Guild — Vulnerable Factory Intranet
> **A Damn Vulnerable Industrial Web Server & CTF Training Lab**

An intentionally vulnerable, Windows 98–themed industrial factory intranet built with **Python (Flask)** and **SQLite**. Designed for cybersecurity education, penetration testing practice, and internal CTF (Capture the Flag) training.

---

## ⚠️ Disclaimer
> **FOR LOCAL EDUCATIONAL USE ONLY**  
> This application contains deliberate security vulnerabilities (SQL Injection, IDOR, Path Traversal, Broken Access Control). **DO NOT** deploy or expose this server on a public network or production environment.

---

## 📑 Table of Contents
1. [Overview & Architecture](#-overview--architecture)
2. [Project Structure](#-project-structure)
3. [Quick Start & Installation](#-quick-start--installation)
4. [Pre-Configured Accounts & Credentials](#-pre-configured-accounts--credentials)
5. [Application Features & Routes](#-application-features--routes)
6. [Security Challenges & Vulnerability Guide](#-security-challenges--vulnerability-guide)
7. [CTF Flags Reference](#-ctf-flags-reference)
8. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🔎 Overview & Architecture

**Blast Furnace Guild** models a legacy manufacturing intranet terminal (styled in authentic Windows 98 / Apex theme) that manages steel smelting operations, shift handover logs, plant grievances, employee performance rankings, technical operating procedures, and facility administration.

Behind its nostalgic interface lie critical web security vulnerabilities matching the OWASP Top 10 categories, demonstrating how legacy architectures, lack of authorization controls, and unvalidated inputs can lead to complete compromise.

```text
BLAST FURNACE GUILD SECURITY LAB
│
├── 01. SQL Injection (Auth Bypass)
│   └── Route: POST /login
│
├── 02. SQL Injection (Search Filter)
│   └── Route: POST /employee-corner
│
├── 03. IDOR (Confidential Profiles)
│   └── Route: GET /profile/<id>
│
├── 04. IDOR (Private Grievance Dispatches)
│   └── Route: GET /grievances/view/<id>
│
├── 05. Path Traversal (Arbitrary File Read)
│   └── Route: GET /document?file=<filename>
│
└── 06. Broken Access Control (Factory Control Center)
    └── Route: GET /admin
```

---

## 📂 Project Structure

```text
Utsav_Server-main/
├── README.md                           # Master documentation
├── factory.db                          # Primary SQLite database
├── flag.txt                            # Root CTF flag (Path Traversal target)
├── vulnerable-factory-dashboard/
│   ├── app.py                          # Flask application logic & routing
│   ├── database.py                     # Database schema definitions & seeding
│   ├── factory.db                      # Local database copy
│   ├── flag.txt                        # Local CTF flag (Path Traversal target)
│   ├── documents/                      # Factory technical documents archive
│   │   ├── safety_manual.txt           # Standard PPE & safety manual
│   │   ├── furnace_procedure.txt       # Operating guidelines for Furnaces 1-4
│   │   ├── emergency_guide.txt         # Evacuation & fire suppression SOP
│   │   ├── maintenance_report.txt      # Asset inspections & maintenance
│   │   └── shift_handover_guide.txt    # Shift rotation & log protocols
│   ├── static/
│   │   ├── style.css                   # Windows 98 desktop theme stylesheet
│   │   ├── photos/                     # Employee badge photos
│   │   └── cctv/                       # CCTV camera stream assets
│   └── templates/                      # Jinja2 HTML templates
│       ├── base.html                   # Desktop taskbar, start menu & explorer
│       ├── login.html                  # Network authentication dialog
│       ├── dashboard.html              # Employee portal home & notices
│       ├── employee_corner.html        # Leaderboard podium & name search
│       ├── profile.html                # Employee personnel record
│       ├── handover.html               # Furnace status & shift log form
│       ├── documents.html              # Factory documents archive listing
│       ├── view_document.html          # Document viewer screen
│       ├── grievances.html             # Grievance dispatch portal
│       ├── view_grievance.html         # Grievance review viewer
│       ├── cctv.html                   # Closed-circuit camera viewer
│       ├── admin.html                  # Factory Control Center
│       └── _msgbox.html                # Win98 error/alert dialog component
```

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- **Python 3.8+**
- **pip**
- **SQLite3** (built into Python standard library)

### 2. Setup Virtual Environment & Dependencies
From the repository root:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install Flask and dependencies
pip install flask
```

### 3. Initialize or Reset Database
To generate or reset the SQLite database with seed data:

```bash
cd vulnerable-factory-dashboard
python database.py
cd ..
```

### 4. Run the Web Server
```bash
flask run --port=8080
         (or)
python vulnerable-factory-dashboard/app.py
```
By default, the server runs on `http://127.0.0.1:5000`.

---

## 🎯 Security Challenges & Vulnerability Guide

### Challenge 01 — SQL Injection (Authentication Bypass)
- **Target URL:** `POST /login`
- **Exploitation:**
  Entering a standard SQL authentication bypass string directly in the username field:
  ```text
  admin' --
  ```
  *(with any password)* forces the query to resolve to:
  ```sql
  SELECT * FROM users WHERE username = 'admin' --' AND password = '...'
  ```
  Logging in directly as `admin` without knowing the password.

---

### Challenge 02 — SQL Injection (Employee Search Filter)
- **Target URL:** `POST /employee-corner`
- **Exploitation:**
  The `search` form field can be injected using single quotes and `UNION SELECT` to extract database contents, table definitions, or credentials:
  ```text
  ' UNION SELECT 1, sql, 'schema', 100 FROM sqlite_master --
  ```

---

### Challenge 03 — Insecure Direct Object Reference (Employee Profiles)
- **Target URL:** `GET /profile/<int:user_id>`
- **Exploitation:**
  Any authenticated employee viewing their own profile (e.g. `/profile/1`) can change the numeric parameter in the URL.
  Accessing user ID `8` (`/profile/8`) loads the profile of **Factory Admin**, revealing their private executive note and flag:
  🚩 **`AxA{1d0r_3xpos3d_th3_adm1n_n0t3}`**

---

### Challenge 04 — Insecure Direct Object Reference (Private Grievance Dispatches)
- **Target URL:** `GET /grievances/view/<int:grievance_id>`
- **Exploitation:**
  The server fetches the grievance solely by `grievance_id` without verifying whether `g.user_id == session["user_id"]` or if the requester is an admin.
  Navigating directly to `/grievances/view/5` reveals management's private confidential grievance dispatch:
  🚩 **`AxA{gr13vance_idor_l3aks_c0nf1dential_notes}`**

---

### Challenge 05 — Path Traversal (Factory Documents Archive)
- **Target URL:** `GET /document?file=<filename>`
- **Exploitation:**
  The endpoint takes the user-supplied `file` parameter and passes it directly to `os.path.join` without stripping directory traversal operators (`../`).
  Requesting:
  ```text
  GET /document?file=../flag.txt
  ```
  breaks out of `documents/` into the application root, reading `flag.txt`:
  🚩 **`AxA{factory_path_traversal}`**

  *Bonus:* An attacker can also read application source files (`../app.py`, `../database.py`) or system files (e.g., `../../../../../../../../etc/passwd`).

---

### Challenge 06 — Broken Access Control (Factory Control Center)
- **Target URL:** `GET /admin`
- **Exploitation:**
  Although the UI hides the "Control Center" button from non-admin accounts, the backend fails to enforce authorization.
  1. Log in as a standard employee (e.g., `geligah` : `summer2024`).
  2. Directly navigate to:
     ```text
     http://127.0.0.1:5000/admin
     ```
  3. The full Factory Control Center loads, exposing:
     - All registered employees, badge IDs, and unmasked salaries
     - Admin internal secret notes
     - All employee grievances across the plant
     - Shift operational notes and furnace statuses

---

## 🏆 CTF Flags Reference

| Flag Identifier | Vulnerability | Exploitation Vector |
| :--- | :--- | :--- |
| `AxA{factory_path_traversal}` | Path Traversal | `GET /document?file=../flag.txt` |
| `AxA{1d0r_3xpos3d_th3_adm1n_n0t3}` | IDOR | `GET /profile/8` *(Admin Profile)* |
| `AxA{gr13vance_idor_l3aks_c0nf1dential_notes}` | IDOR | `GET /grievances/view/5` *(Confidential Note)* |

---