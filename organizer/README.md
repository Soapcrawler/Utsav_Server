**A damn vulnerable server!**

# FACTORY SECURITY LAB
```text
FACTORY SECURITY LAB
│
├── 01. SQL Injection
│   └── Login
│
├── 02. SQL Injection
│   └── Employee Search
│
├── 03. IDOR
│   └── Employee Profiles
│
├── 04. IDOR
│   └── Grievances
│
├── 05. Path Traversal
│   └── Factory Documents
│
└── 06. Broken Access Control
    └── Factory Admin Panel


----

# NOTICES & ALERTS (organizer only)

Participants see a read-only **Notices & Alerts** page after logging in.
Posts are added from the organizer machine with `post_notice.py`
(keep it outside the deployed project folder):

    python post_notice.py "Furnace 2 overheating" --photo furnace2.png --level Critical
    python post_notice.py "Shift change in 10 minutes"
    python post_notice.py --list
    python post_notice.py --delete 3

Levels: Info, Warning, Critical. New posts show up on open pages within ~8 seconds.
Data lives in `deploy/vulnerable-factory-dashboard/notices/` (images + `notices.json`), no database.
For several instances, set the same `NOTICES_DIR` for every instance and for this script.
