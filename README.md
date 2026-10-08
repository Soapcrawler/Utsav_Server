FORGE & FRACTURE PACKAGE

A CTF-style web app for a cybersecurity event. Participants attack a deliberately vulnerable "factory dashboard" (a Flask app for a fictional smelting plant) to find flags hidden behind intentional vulnerabilities, then combine them to unlock a hidden reward page.

Layout

forge-and-fracture/ ├── README.md this file ├── deploy/ │ └── vulnerable-factory-dashboard/ what each participant instance runs │ ├── app.py Flask app / all routes │ ├── database.py seeds factory.db with users, grievances, etc. │ ├── requirements.txt │ ├── flag.txt path-traversal target │ ├── documents/ factory documents (path traversal challenge) │ ├── static/ css, photos, CCTV gif │ ├── templates/ HTML pages │ └── notices/ organizer-posted notices (images + notices.json) └── organizer/ organizer-only — do NOT deploy ├── README.md challenge list, flags, reward-page details └── post_notice.py posts live notices during the event

Challenges

Six challenges, five of which award a flag (full details, flag values, and the reward-page URL are in organizer/README.md):

SQL Injection — Login (demonstration only, no flag)
SQL Injection — Employee Search
IDOR — Employee Profiles
IDOR — Grievances
Path Traversal — Factory Documents
Broken Access Control — Factory Admin Panel (no flag of its own)

Plus two optional extras: a flag visible via Inspect Element on the CCTV page, and a standalone bonus flag in /robots.txt (unrelated to the others, not required to finish).

Collecting the five numbered flags and visiting the URL formed by concatenating them in order (/{flag_001}{flag_002}...{flag_005}) unlocks a hidden reward page.

Running an instance
cd deploy/vulnerable-factory-dashboard
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py          # http://localhost:5000

For several simultaneous instances, see organizer/README.md for the NOTICES_DIR setting used by live notices.

Content
forge-and-fracture.zip

ZIP

forge-and-fracture.zip

ZIP
