
import hmac
import json
import os
import sqlite3
from datetime import date
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, g,
    jsonify, send_from_directory, abort,
)

from database import HANDOVER_SCHEMA

app = Flask(__name__)
app.secret_key = "factory-dashboard-dev-secret"

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "factory.db")
DATABASE = DB_FILE if os.path.exists(DB_FILE) else "factory.db"

# Factory Documents
DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "documents")
# Containment for the path-traversal challenge: only documents/ and flag.txt may be read.
DOCUMENTS_REAL = os.path.realpath(DOCUMENTS_DIR)
FLAG_FILE = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "flag.txt"))
FACTORY_DOCUMENTS = [
    {
        "title": "Safety Manual",
        "filename": "safety_manual.txt",
        "description": "Standard safety regulations, PPE requirements, and hazard management protocols.",
    },
    {
        "title": "Furnace Operating Procedure",
        "filename": "furnace_procedure.txt",
        "description": "Operational guidelines, thermal limits, and ignition SOPs for Furnaces 1 through 4.",
    },
    {
        "title": "Emergency Response Guide",
        "filename": "emergency_guide.txt",
        "description": "Evacuation steps, fire suppression protocols, and emergency medical contacts.",
    },
    {
        "title": "Maintenance Report",
        "filename": "maintenance_report.txt",
        "description": "Quarterly inspection report, asset integrity logs, and scheduled mechanical service.",
    },
    {
        "title": "Shift Handover Guide",
        "filename": "shift_handover_guide.txt",
        "description": "Standard procedures for shift rotations, furnace logging, and handover signoffs.",
    },
]

# Podium photos live in static/photos/<username>.<ext>
PHOTO_DIR = os.path.join(app.static_folder, "photos")
PHOTO_EXTS = ("jpg", "jpeg", "png", "webp", "gif")


def photo_for(username):
    for ext in PHOTO_EXTS:
        if os.path.exists(os.path.join(PHOTO_DIR, "{}.{}".format(username, ext))):
            return url_for("static", filename="photos/{}.{}".format(username, ext))
    return url_for("static", filename="photos/default.svg")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


ROBOTS_TXT = (
    "User-agent: *\n"
    "Disallow: /admin\n"
    "Disallow: /handover\n"
    "# audit trail: AxA{r0b0ts_t0ld_y0u_n0t_t0_l00k_b0nus}\n"
)


@app.route("/robots.txt")
def robots_txt():
    # Bonus flag only - not part of FINAL_FLAGS, not required to reach the reward page.
    return app.response_class(ROBOTS_TXT, mimetype="text/plain")


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        #sqli
        db = get_db()
        query = "SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(
            username, password
        )
        try:
            user = db.execute(query).fetchone()
        except sqlite3.Error as e:
            user = None
            flash(f"Query error: {e}")

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return render_template("dashboard.html", user=user)


@app.route("/profile/<int:user_id>")
@login_required
def profile(user_id):
    #idor
    db = get_db()
    employee = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

    if employee is None:
        flash("Employee not found.")
        return redirect(url_for("dashboard"))

    is_self = employee["id"] == session["user_id"]
    return render_template("profile.html", employee=employee, is_self=is_self)


@app.route("/employee-corner", methods=["GET", "POST"])
@login_required
def employee_corner():
    db = get_db()

    top_rows = db.execute(
        "SELECT * FROM users WHERE role = 'employee' "
        "ORDER BY performance_score DESC, id ASC LIMIT 3"
    ).fetchall()
    top = []
    for rank, row in enumerate(top_rows, start=1):
        emp = dict(row)
        emp["rank"] = rank
        emp["photo"] = photo_for(emp["username"])
        top.append(emp)

    # Podium display order: 2nd place on the left, 1st in the middle, 3rd on the right.
    podium = [top[i] for i in (1, 0, 2) if i < len(top)]

    results = None
    search_term = ""
    if request.method == "POST":
        search_term = request.form.get("search", "")

        #sqli
        query = (
            "SELECT id, full_name, department, performance_score "
            "FROM users WHERE full_name LIKE '%{}%'".format(search_term)
        )
        try:
            results = db.execute(query).fetchall()
        except sqlite3.Error as e:
            results = []
            flash(f"Query error: {e}")


    return render_template(
        "employee_corner.html",
        podium=podium,
        results=results,
        search_term=search_term,
    )


@app.route("/grievances", methods=["GET", "POST"])
@login_required
def grievances():
    db = get_db()
    if request.method == "POST":
        subject = request.form.get("subject", "")
        message = request.form.get("message", "")
        db.execute(
            "INSERT INTO grievances (user_id, subject, message, status) VALUES (?, ?, ?, ?)",
            (session["user_id"], subject, message, "Pending"),
        )
        db.commit()
        flash("Your grievance has been submitted.")
        return redirect(url_for("grievances"))

    my_grievances = db.execute(
        "SELECT * FROM grievances WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    return render_template("grievances.html", grievances=my_grievances)


@app.route("/grievances/view/<int:grievance_id>")
@login_required
def view_grievance(grievance_id):
    #idor
    db = get_db()
    grievance = db.execute(
        "SELECT g.*, u.full_name, u.username FROM grievances g "
        "JOIN users u ON g.user_id = u.id WHERE g.id = ?",
        (grievance_id,),
    ).fetchone()
    # -------------------------------------------------------------------

    if grievance is None:
        flash("Grievance not found.")
        return redirect(url_for("grievances"))

    is_own = grievance["user_id"] == session["user_id"]
    return render_template("view_grievance.html", grievance=grievance, is_own=is_own)


FURNACE_STATUSES = ("Running", "Idle", "Under Maintenance", "Shutdown")
ATTENDANCE_TOTAL = 30


@app.route("/handover", methods=["GET", "POST"])
@login_required
def handover():
    db = get_db()
    db.executescript(HANDOVER_SCHEMA)

    if request.method == "POST":
        shift_date = request.form.get("shift_date", "").strip()
        work_order = request.form.get("work_order", "").strip()
        furnaces = [request.form.get("furnace_{}".format(i), "") for i in range(1, 5)]
        accidents = request.form.get("accidents", "")
        attendance = request.form.get("attendance", "").strip()

        error = None
        try:
            date.fromisoformat(shift_date)
        except ValueError:
            error = "Please enter a valid shift date."
        if error is None and not work_order:
            error = "Please enter the current work order."
        if error is None and any(f not in FURNACE_STATUSES for f in furnaces):
            error = "Please choose a status for every furnace."
        if error is None and accidents not in ("Yes", "No"):
            error = "Please state whether there were any accidents."
        if error is None and not (
            attendance.isdigit() and 0 <= int(attendance) <= ATTENDANCE_TOTAL
        ):
            error = "Attendance must be a number from 0 to {}.".format(ATTENDANCE_TOTAL)

        if error:
            flash(error)
        else:
            db.execute(
                "INSERT INTO handover_notes (user_id, shift_date, work_order, furnace_1, "
                "furnace_2, furnace_3, furnace_4, accidents, attendance) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session["user_id"], shift_date, work_order, *furnaces, accidents, int(attendance)),
            )
            db.commit()
            flash("Shift handover note saved.")
            return redirect(url_for("handover"))

    notes = db.execute(
        "SELECT h.*, u.full_name FROM handover_notes h JOIN users u ON h.user_id = u.id "
        "ORDER BY h.shift_date DESC, h.id DESC"
    ).fetchall()
    return render_template(
        "handover.html",
        notes=notes,
        statuses=FURNACE_STATUSES,
        total=ATTENDANCE_TOTAL,
        today=date.today().isoformat(),
    )


# Notices / Alerts (read-only here; posts are added by the event owner)
# Set NOTICES_DIR to point several instances at one shared folder.
NOTICES_DIR = os.environ.get(
    "NOTICES_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "notices")
)
NOTICES_INDEX = os.path.join(NOTICES_DIR, "notices.json")
NOTICE_PHOTO_EXTS = ("jpg", "jpeg", "png", "webp", "gif")


def load_notices():
    try:
        with open(NOTICES_INDEX, "r", encoding="utf-8") as f:
            items = json.load(f)
    except (OSError, ValueError):
        return []
    return sorted(items, key=lambda n: n.get("id", 0), reverse=True)


@app.route("/notices")
@login_required
def notices():
    return render_template("notices.html", notices=load_notices())


@app.route("/notices/feed")
@login_required
def notices_feed():
    items = load_notices()
    return jsonify({"latest": items[0]["id"] if items else 0, "count": len(items)})


@app.route("/notices/photo/<name>")
@login_required
def notice_photo(name):
    # Only serve filenames that the index lists, so the folder isn't browsable.
    if name not in {n.get("photo") for n in load_notices()}:
        abort(404)
    return send_from_directory(NOTICES_DIR, name)


# CCTV feed
CCTV_DIR = os.path.join(app.static_folder, "cctv")


@app.route("/cctv")
@login_required
def cctv():
    cam1 = None
    path = os.path.join(CCTV_DIR, "cam1.gif")
    if os.path.exists(path):
        # ?v=<mtime> so a replaced GIF shows up without a hard refresh
        cam1 = url_for("static", filename="cctv/cam1.gif", v=int(os.path.getmtime(path)))
    return render_template("cctv.html", cam1=cam1)


# Factory Documents
@app.route("/documents")
@login_required
def documents():
    return render_template("documents.html", documents=FACTORY_DOCUMENTS)


@app.route("/document")
@login_required
def view_document():
    filename = request.args.get("file", "")
    if not filename:
        flash("No document specified.")
        return redirect(url_for("documents"))

    # INTENTIONAL VULNERABILITY: Path Traversal
    # 'file' is joined to DOCUMENTS_DIR without stripping '../', so '../flag.txt' works.
    # Containment: the resolved real path must be inside documents/ or be flag.txt itself,
    # so traversal cannot reach source code, the database, templates, or anything outside
    # the app (/etc/passwd and friends). Failures all look the same, so nothing leaks.
    try:
        filepath = os.path.realpath(os.path.join(DOCUMENTS_DIR, filename))
        if not (filepath.startswith(DOCUMENTS_REAL + os.sep) or filepath == FLAG_FILE):
            raise PermissionError
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, ValueError):
        flash("Document not found.")
        return redirect(url_for("documents"))

    return render_template("view_document.html", filename=filename, content=content)


@app.route("/admin")
@login_required
def admin_panel():
    # INTENTIONAL VULNERABILITY: Broken Access Control / Missing Function-Level Authorization
    # The endpoint checks authentication via @login_required, but intentionally omits
    # the authorization check: if session.get("role") != "admin": ...
    # This allows any logged-in user (including employees) to access the Factory Control Center.
    db = get_db()
    all_users = db.execute("SELECT * FROM users ORDER BY id ASC").fetchall()
    all_grievances = db.execute(
        "SELECT g.*, u.full_name, u.username FROM grievances g JOIN users u ON g.user_id = u.id ORDER BY g.id DESC"
    ).fetchall()
    handovers = db.execute(
        "SELECT h.*, u.full_name FROM handover_notes h JOIN users u ON h.user_id = u.id ORDER BY h.shift_date DESC LIMIT 5"
    ).fetchall()

    total_employees = len(all_users)
    pending_grievances = sum(1 for g in all_grievances if g["status"] == "Pending")

    dept_counts = {}
    for u in all_users:
        dept = u["department"] or "General"
        dept_counts[dept] = dept_counts.get(dept, 0) + 1

    return render_template(
        "admin.html",
        users=all_users,
        grievances=all_grievances,
        handovers=handovers,
        total_employees=total_employees,
        pending_grievances=pending_grievances,
        dept_counts=dept_counts,
    )



# Hidden final page
# Opens only at /<flag_001><flag_002>...<flag_005> (all flags concatenated, in this order).
# The _NNN suffix on each flag tells participants where it slots into the URL.
FINAL_FLAGS = [
    "AxA{un10n_s3l3ct_dr41ns_th3_v4ult_001}",                  # flag_001 - employee search SQLi
    "AxA{1d0r_3xpos3d_th3_adm1n_n0t3_002}",                    # flag_002 - profile IDOR
    "AxA{gr13vance_idor_l3aks_c0nf1dential_notes_003}",        # flag_003 - grievance IDOR
    "AxA{F4CT0RY_P47H_7R4V3RS4L_004}",                         # flag_004 - path traversal
    "AxA{1ns3ct_3l3m3nt_r3v34ls_th3_c4m3r4_n0t3_005}",         # flag_005 - CCTV inspect element
]
FINAL_PATH = "".join(FINAL_FLAGS)


@app.route("/<path:secret>")
def final_page(secret):
    # Anything that isn't the exact flag chain is a plain 404, so the page stays hidden.
    if not hmac.compare_digest(secret.encode("utf-8"), FINAL_PATH.encode("utf-8")):
        abort(404)
    return render_template("final.html")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
