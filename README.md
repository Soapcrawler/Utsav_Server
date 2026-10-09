# Utsav Server

A Flask-based vulnerable factory intranet for security labs and CTF exercises.

## Features

- Employee login and profiles
- Employee search
- Grievances and shift handover notes
- Factory documents and CCTV page
- Admin control center
- Deliberate vulnerabilities including SQL injection, IDOR, path traversal, and broken access control

## Run locally

```bash
cd deploy/vulnerable-factory-dashboard
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`.

Organizer notices are managed with `organizer/post_notice.py`.
