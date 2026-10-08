FORGE & FRACTURE PACKAGE

deploy/      what participants' instances run   -> deploy/vulnerable-factory-dashboard
organizer/   organizer-only files (do NOT deploy) -> README.md, post_notice.py

Run the site:
  cd deploy/vulnerable-factory-dashboard
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python app.py          # http://localhost:5000

FACTORY SECURITY LAB
│
├── 01. SQL Injection
│   └── Login                      (demonstration only - no flag of its own)
│
├── 02. SQL Injection
│   └── Employee Search            -> flag_001
│
├── 03. IDOR
│   └── Employee Profiles          -> flag_002
│
├── 04. IDOR
│   └── Grievances                 -> flag_003
│
├── 05. Path Traversal
│   └── Factory Documents          -> flag_004
│
├── 06. Broken Access Control
│   └── Factory Admin Panel        (no flag of its own - exposes flag_002 again)
│
└── Bonus. Inspect Element
    └── CCTV Page                  -> flag_005
