"""HRMS - a small Flask app for employees, attendance and monthly exports.

Storage is plain JSON files in the data/ folder. No login, no database.

Run:  python app.py   ->   http://127.0.0.1:5000
"""

from __future__ import annotations

import calendar
import csv
import io
import json
from datetime import date, timedelta
from pathlib import Path

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# "Leave" = approved leave (manually marked), not an absence.
STATUSES = ("Present", "Late", "Absent", "Leave")
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
EXPORT_HEADERS = [
    "Employee ID", "Name", "Department", "Designation", "Date", "Status", "Hours",
]

app = Flask(__name__)
# secret_key is only used for one-shot flash messages; there is no login.
app.secret_key = "hrms-local-only"


# ------------------------------------------------------------------ storage --
def _load(filename: str, default):
    path = DATA_DIR / filename
    if not path.exists():
        return default
    try:
        # utf-8-sig: also reads files that start with a UTF-8 BOM (e.g. edited
        # in PowerShell/Excel) instead of failing and silently using empty data.
        with path.open(encoding="utf-8-sig") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        flash(f"WARNING: could not read {filename} ({exc}). Using empty data.", "error")
        return default


def _save(filename: str, data) -> None:
    path = DATA_DIR / filename
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    tmp.replace(path)


def load_config() -> dict:
    cfg = _load("config.json", {})
    cfg.setdefault("LATE_TIME", "22:00")
    # Weekday names that are never auto-marked absent (e.g. ["Saturday"] or
    # ["Saturday", "Sunday"]). Edit data/config.json to change.
    cfg.setdefault("OFF_DAYS", ["Saturday"])
    return cfg


def load_employees() -> list[dict]:
    return _load("employees.json", {"employees": []}).get("employees", [])


def save_employees(employees: list[dict]) -> None:
    _save("employees.json", {"employees": employees})


def load_attendance() -> dict:
    return _load("attendance.json", {"records": {}}).get("records", {})


def save_attendance(records: dict) -> None:
    _save("attendance.json", {"records": records})


# ----------------------------------------------------------------- helpers --
def next_employee_id(employees: list[dict]) -> str:
    used = []
    for emp in employees:
        emp_id = str(emp.get("id", ""))
        if emp_id.startswith("emp_") and emp_id[4:].isdigit():
            used.append(int(emp_id[4:]))
    return f"emp_{(max(used) + 1) if used else 1:03d}"


def to_minutes(hhmm: str) -> int:
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


def attendance_status(arrival: str, late_time: str) -> str:
    return "Late" if to_minutes(arrival) > to_minutes(late_time) else "Present"


def export_rows(year: int, month: int) -> list[list]:
    """Rows for one month, sorted by date then employee id."""
    prefix = f"{year:04d}-{month:02d}"
    employees = {e["id"]: e for e in load_employees()}
    rows = []
    for emp_id, days in load_attendance().items():
        emp = employees.get(emp_id, {})
        for day, rec in days.items():
            if not str(day).startswith(prefix):
                continue
            rows.append([
                emp_id,
                emp.get("name", ""),
                emp.get("department", ""),
                emp.get("designation", ""),
                day,
                rec.get("status", ""),
                rec.get("hours", 0),
            ])
    rows.sort(key=lambda r: (r[4], r[0]))
    return rows


def materialize_absents(year: int, month: int) -> tuple[int, list]:
    """Save a default 'Absent' record for every unmarked working day of the month.

    Called from the export page, so attendance.json and the download always match.

    Rules:
      - past days only (a future/current-month day is never guessed);
      - OFF_DAYS (data/config.json, default Saturday) are never filled;
      - active employees: filled from max(month start, added_on);
      - ex employees: only up to their last marked day of that month
        (nothing is guessed for months they never worked);
      - records you already marked are never overwritten - change them
        (e.g. to Approved leave) on the attendance page.

    Returns (number of records written, off day names).
    """
    cfg = load_config()
    off_days = [str(d).strip() for d in cfg.get("OFF_DAYS", []) if str(d).strip()]
    off_names = {d.lower() for d in off_days}
    employees = load_employees()
    month_start = date(year, month, 1)
    month_end = date(year, month, calendar.monthrange(year, month)[1])
    last_allowed = min(month_end, date.today())
    if not employees or last_allowed < month_start:
        return 0, off_days

    prefix = f"{year:04d}-{month:02d}"
    records = load_attendance()
    filled = 0
    for emp in employees:
        existing = records.get(emp["id"], {})
        emp_start = month_start
        added = str(emp.get("added_on", "")).strip()
        if added:
            try:
                emp_start = max(emp_start, date.fromisoformat(added))
            except ValueError:
                pass
        emp_end = last_allowed
        if not emp.get("active", True):
            marked = []
            for key in existing:
                if str(key).startswith(prefix):
                    try:
                        marked.append(date.fromisoformat(str(key)))
                    except ValueError:
                        continue
            if not marked:
                continue  # ex employee, no marks this month -> guess nothing
            emp_end = min(max(marked), last_allowed)
        additions = {}
        cursor = emp_start
        while cursor <= emp_end:
            iso = cursor.isoformat()
            if cursor.strftime("%A").lower() not in off_names and iso not in existing:
                additions[iso] = {"arrival": "", "hours": 0.0, "status": "Absent"}
            cursor += timedelta(days=1)
        if additions:
            records.setdefault(emp["id"], {}).update(additions)
            filled += len(additions)
    if filled:
        save_attendance(records)
    return filled, off_days


def make_csv(rows: list[list]) -> io.BytesIO:
    buf = io.StringIO()
    writer = csv.writer(buf)  # comma separated, quoted when needed, CRLF lines
    writer.writerow(EXPORT_HEADERS)
    writer.writerows(rows)
    # utf-8-sig (BOM) so Google Sheets / Excel detect the encoding correctly.
    return io.BytesIO(buf.getvalue().encode("utf-8-sig"))


def make_xlsx(rows: list[list]) -> io.BytesIO:
    wb = Workbook()
    ws = wb.active
    ws.title = "Attendance"

    header_fill = PatternFill("solid", fgColor="1F4E78")
    header_font = Font(bold=True, color="FFFFFF")
    status_colors = {
        "Present": PatternFill("solid", fgColor="E2EFDA"),
        "Late": PatternFill("solid", fgColor="FFF2CC"),
        "Absent": PatternFill("solid", fgColor="FCE4E4"),
        "Leave": PatternFill("solid", fgColor="DDEBF7"),
    }

    ws.append(EXPORT_HEADERS)
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")

    for row in rows:
        ws.append(row)
        status_cell = ws.cell(row=ws.max_row, column=6)
        if status_cell.value in status_colors:
            status_cell.fill = status_colors[status_cell.value]

    for index, header in enumerate(EXPORT_HEADERS, start=1):
        letter = get_column_letter(index)
        width = max([len(str(header))] + [len(str(r[index - 1])) for r in rows]) + 4
        ws.column_dimensions[letter].width = min(max(width, 10), 40)

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(EXPORT_HEADERS))}{ws.max_row}"

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out


# -------------------------------------------------------------------- pages --
@app.route("/")
def index():
    employees = load_employees()
    records = load_attendance()
    total_records = sum(len(days) for days in records.values())
    return render_template(
        "index.html",
        active=sum(1 for e in employees if e.get("active", True)),
        ex=len(employees) - sum(1 for e in employees if e.get("active", True)),
        total_records=total_records,
    )


@app.route("/employees", methods=["GET", "POST"])
def employees_page():
    employees = load_employees()
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Name is required.", "error")
        else:
            emp = {
                "id": next_employee_id(employees),
                "name": name,
                "department": (request.form.get("department") or "").strip(),
                "designation": (request.form.get("designation") or "").strip(),
                "active": True,
                "added_on": date.today().isoformat(),
            }
            employees.append(emp)
            save_employees(employees)
            flash(f"Added {emp['id']} - {name}.", "ok")
        return redirect(url_for("employees_page"))
    return render_template("employees.html", employees=employees)


@app.post("/employees/<emp_id>/toggle")
def employee_toggle(emp_id):
    employees = load_employees()
    for emp in employees:
        if emp["id"] == emp_id:
            emp["active"] = not emp.get("active", True)
            save_employees(employees)
            state = "ACTIVE" if emp["active"] else "ex-employee"
            flash(f"{emp_id} is now {state}. Attendance history is kept.", "ok")
            break
    else:
        flash(f"Employee {emp_id} not found.", "error")
    return redirect(url_for("employees_page"))


@app.post("/employees/<emp_id>/delete")
def employee_delete(emp_id):
    employees = load_employees()
    kept = [e for e in employees if e["id"] != emp_id]
    if len(kept) == len(employees):
        flash(f"Employee {emp_id} not found.", "error")
        return redirect(url_for("employees_page"))
    save_employees(kept)
    records = load_attendance()
    removed = len(records.pop(emp_id, {}))
    if removed:
        save_attendance(records)
    flash(
        f"Deleted {emp_id} and {removed} attendance record(s). "
        "Tip: use 'Mark ex' next time to keep the history.",
        "ok",
    )
    return redirect(url_for("employees_page"))


@app.route("/attendance", methods=["GET", "POST"])
def attendance_page():
    employees = load_employees()
    cfg = load_config()
    if request.method == "POST":
        emp_id = (request.form.get("emp_id") or "").strip()
        day = (request.form.get("day") or "").strip()
        day_type = (request.form.get("day_type") or "worked").strip()
        arrival = (request.form.get("arrival") or "").strip()
        hours_raw = (request.form.get("hours") or "").strip()

        known = {e["id"] for e in employees}
        error = None
        if emp_id not in known:
            error = "Pick a valid employee."
        else:
            try:
                date.fromisoformat(day)
            except ValueError:
                error = "Date must be valid (YYYY-MM-DD)."

        record = None
        if not error:
            if day_type == "absent":
                record = {"arrival": "", "hours": 0.0, "status": "Absent"}
            elif day_type == "leave":
                record = {"arrival": "", "hours": 0.0, "status": "Leave"}
            else:
                if not arrival:
                    error = "Arrival time is required (or pick leave/absent as the day type)."
                else:
                    try:
                        hours = float(hours_raw or "0")
                    except ValueError:
                        hours = -1
                    if not 0 <= hours <= 24:
                        error = "Hours must be a number between 0 and 24."
                    else:
                        record = {
                            "arrival": arrival,
                            "hours": hours,
                            "status": attendance_status(arrival, cfg["LATE_TIME"]),
                        }

        if error:
            flash(error, "error")
        else:
            records = load_attendance()
            existed = day in records.get(emp_id, {})
            records.setdefault(emp_id, {})[day] = record
            save_attendance(records)
            action = "Updated" if existed else "Saved"
            flash(f"{action} {emp_id} on {day}: {record['status']}.", "ok")
        return redirect(url_for("attendance_page", emp_id=emp_id, day=day))

    return render_template(
        "attendance.html",
        employees=employees,
        selected_emp=request.args.get("emp_id", ""),
        selected_day=request.args.get("day") or date.today().isoformat(),
        late_time=cfg["LATE_TIME"],
    )


@app.get("/api/attendance")
def api_attendance():
    emp_id = request.args.get("emp_id", "")
    day = request.args.get("date", "")
    record = load_attendance().get(emp_id, {}).get(day)
    return jsonify({"found": record is not None, "record": record or {}})


@app.route("/export")
def export_page():
    today = date.today()
    try:
        month = int(request.args.get("month", today.month))
        year = int(request.args.get("year", today.year))
    except ValueError:
        month, year = today.month, today.year

    filled, off_days = materialize_absents(year, month)
    if filled:
        flash(
            f"Auto-filled {filled} unmarked working day(s) as Absent "
            f"(off days skipped: {', '.join(off_days) or 'none'}).",
            "ok",
        )
    count = len(export_rows(year, month))
    return render_template(
        "export.html",
        month=month,
        year=year,
        count=count,
        months=MONTH_NAMES,
        today=today,
        off_days=off_days,
        late_time=load_config()["LATE_TIME"],
    )


@app.get("/export/download")
def export_download():
    today = date.today()
    try:
        month = int(request.args.get("month", today.month))
        year = int(request.args.get("year", today.year))
    except ValueError:
        month, year = today.month, today.year
    fmt = request.args.get("format", "csv")

    rows = export_rows(year, month)
    if not rows:
        flash(f"No attendance records for {MONTH_NAMES[month - 1]} {year}.", "error")
        return redirect(url_for("export_page", month=month, year=year))

    stamp = f"{year:04d}-{month:02d}"
    if fmt == "xlsx":
        payload = make_xlsx(rows)
        return send_file(
            payload,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=f"attendance_{stamp}.xlsx",
        )
    payload = make_csv(rows)
    return send_file(
        payload, mimetype="text/csv", as_attachment=True,
        download_name=f"attendance_{stamp}.csv",
    )


@app.route("/import", methods=["GET", "POST"])
def import_page():
    if request.method != "POST":
        return render_template("import.html")

    file = request.files.get("file")
    if not file or not file.filename.lower().endswith(".json"):
        flash("Choose a .json file to import.", "error")
        return redirect(url_for("import_page"))
    try:
        payload = json.load(io.BytesIO(file.read()))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        flash(f"Could not parse the file as JSON: {exc}", "error")
        return redirect(url_for("import_page"))
    if not isinstance(payload, dict):
        flash("Top level of the JSON must be an object with 'employees' / 'attendance'.", "error")
        return redirect(url_for("import_page"))

    stats = {"emp_new": 0, "emp_updated": 0, "att_new": 0, "att_updated": 0}
    skipped = []

    # employees -----------------------------------------------------------
    employees = load_employees()
    if isinstance(payload.get("employees"), list):
        for item in payload["employees"]:
            if not isinstance(item, dict) or not str(item.get("name", "")).strip():
                skipped.append(f"employee without name: {item!r}")
                continue
            emp_id = str(item.get("id", "")).strip()
            existing = next((e for e in employees if e["id"] == emp_id), None)
            if existing:
                for field in ("name", "department", "designation"):
                    if str(item.get(field, "")).strip():
                        existing[field] = str(item[field]).strip()
                if isinstance(item.get("active"), bool):
                    existing["active"] = item["active"]
                stats["emp_updated"] += 1
            else:
                if not (emp_id.startswith("emp_") and emp_id[4:].isdigit()):
                    emp_id = next_employee_id(employees)
                active = item.get("active", True)
                employees.append({
                    "id": emp_id,
                    "name": str(item["name"]).strip(),
                    "department": str(item.get("department", "")).strip(),
                    "designation": str(item.get("designation", "")).strip(),
                    "active": active if isinstance(active, bool) else str(active).lower() != "false",
                    "added_on": str(item.get("added_on", date.today().isoformat())),
                })
                stats["emp_new"] += 1
        save_employees(employees)

    # attendance ----------------------------------------------------------
    if isinstance(payload.get("attendance"), dict):
        cfg = load_config()
        known = {e["id"] for e in employees}
        records = load_attendance()
        for emp_id, days in payload["attendance"].items():
            if emp_id not in known:
                skipped.append(f"attendance for unknown employee: {emp_id}")
                continue
            if not isinstance(days, dict):
                skipped.append(f"attendance for {emp_id} is not an object")
                continue
            for day, rec in days.items():
                try:
                    date.fromisoformat(str(day))
                except ValueError:
                    skipped.append(f"bad date {day} for {emp_id}")
                    continue
                if not isinstance(rec, dict):
                    skipped.append(f"bad record {emp_id} {day}")
                    continue
                status = str(rec.get("status", "")).strip()
                if status not in STATUSES:
                    arrival = str(rec.get("arrival", "")).strip()
                    status = (
                        attendance_status(arrival, cfg["LATE_TIME"])
                        if arrival else "Absent"
                    )
                try:
                    hours = float(rec.get("hours", 0) or 0)
                except (TypeError, ValueError):
                    hours = 0.0
                existed = str(day) in records.get(emp_id, {})
                records.setdefault(emp_id, {})[str(day)] = {
                    "arrival": str(rec.get("arrival", "")).strip(),
                    "hours": hours,
                    "status": status,
                }
                stats["att_updated" if existed else "att_new"] += 1
        save_attendance(records)

    if not payload.get("employees") and not payload.get("attendance"):
        skipped.append("nothing to do: JSON has no 'employees' or 'attendance' key")

    flash(
        "Import done: {emp_new} employee(s) added, {emp_updated} updated, "
        "{att_new} attendance record(s) added, {att_updated} updated.".format(**stats),
        "ok",
    )
    for note in skipped[:10]:
        flash(f"Skipped: {note}", "error")
    return redirect(url_for("import_page"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
