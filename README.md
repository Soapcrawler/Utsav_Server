FORGE & FRACTURE PACKAGE

deploy/      what participants' instances run   -> deploy/vulnerable-factory-dashboard
organizer/   organizer-only files (do NOT deploy) -> README.md, post_notice.py

Run the site:
  cd deploy/vulnerable-factory-dashboard
  python -m venv .venv && source .venv/bin/activate
  pip install -r requirements.txt
  python app.py          # http://localhost:5000
