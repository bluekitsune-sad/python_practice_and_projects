"""End-to-end smoke test for the HRMS app. Run from the HRMS folder:

    python smoke_test.py

It exercises every route against a TEMPORARY data folder, so your real
data/ files are never touched. Prints PASS/FAIL per check, exit code 1 on failure.
"""

from __future__ import annotations

import io
import json
import shutil
import tempfile
from pathlib import Path

import app as app_module

BASE = Path(__file__).resolve().parent
results: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, extra: str = "") -> None:
    results.append((name, bool(condition), extra))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="hrms_smoke_"))
    app_module.DATA_DIR = tmp
    shutil.copy(BASE / "data" / "config.json", tmp / "config.json")
    client = app_module.app.test_client()

    # pages ---------------------------------------------------------------
    for route in ("/", "/employees", "/attendance", "/export", "/import"):
        resp = client.get(route)
        check(f"GET {route} -> 200", resp.status_code == 200, str(resp.status_code))

    # employees -----------------------------------------------------------
    resp = client.post("/employees", data={
        "name": "Ali Khan", "department": "Operations", "designation": "Supervisor",
    }, follow_redirects=True)
    check("add employee 1", b"emp_001" in resp.data and resp.status_code == 200)
    resp = client.post("/employees", data={"name": "Sara Ahmed"}, follow_redirects=True)
    check("add employee 2 (minimal)", b"emp_002" in resp.data)
    resp = client.post("/employees", data={"name": ""}, follow_redirects=True)
    check("empty name rejected", b"Name is required" in resp.data)
    check("IDs auto-generated", json.loads((tmp / "employees.json").read_text("utf-8"))["employees"][0]["id"] == "emp_001")

    # attendance ----------------------------------------------------------
    def save(day: str, arrival: str, hours: str, absent: str | None = None) -> str:
        data = {"emp_id": "emp_001", "day": day, "arrival": arrival, "hours": hours}
        if absent:
            data["absent"] = absent
        return client.post("/attendance", data=data, follow_redirects=True).data.decode("utf-8")

    out = save("2026-10-01", "09:00", "8")
    check("on-time -> Present", "Saved emp_001 on 2026-10-01: Present." in out)
    out = save("2026-10-02", "22:30", "8")
    check("after 22:00 -> Late", "Late" in out)
    out = save("2026-10-03", "", "0", absent="on")
    check("absent saved", "Absent" in out)
    out = save("2026-10-01", "09:30", "7.5")
    check("re-save shows Update", "Updated emp_001 on 2026-10-01" in out)
    out = save("2026-10-04", "", "8")
    check("missing arrival rejected", "Arrival time is required" in out)
    out = save("bad-date", "09:00", "8")
    check("bad date rejected", "Date must be valid" in out)

    resp = client.get("/api/attendance?emp_id=emp_001&date=2026-10-01")
    payload = resp.get_json()
    check("existing-record API", payload["found"] and payload["record"]["hours"] == 7.5)
    resp = client.get("/api/attendance?emp_id=emp_001&date=2026-10-09")
    check("existing-record API (missing day)", resp.get_json()["found"] is False)

    # export CSV ----------------------------------------------------------
    resp = client.get("/export/download?month=10&year=2026&format=csv")
    raw = resp.data
    check("csv 200", resp.status_code == 200)
    check("csv filename", resp.headers["Content-Disposition"].endswith('attendance_2026-10.csv'))
    check("csv has UTF-8 BOM (Google Sheets/Excel friendly)", raw.startswith(b"\xef\xbb\xbf"))
    text = raw.decode("utf-8-sig")
    check("csv header", text.splitlines()[0] == "Employee ID,Name,Department,Designation,Date,Status,Hours")
    check("csv 3 data rows", len(text.splitlines()) == 4, f"{len(text.splitlines())} lines")
    check("csv contains updated value", "2026-10-01,Present,7.5" in text.replace('"', ""))
    check("csv contains Late + Absent rows", "Late" in text and "Absent" in text)
    sample_csv = app_module.make_csv(
        [["emp_009", "Khan, Ali", "", "", "2026-11-01", "Present", 8]]
    ).getvalue().decode("utf-8-sig")
    check("csv quotes names containing commas", '"Khan, Ali"' in sample_csv)

    # export XLSX ---------------------------------------------------------
    resp = client.get("/export/download?month=10&year=2026&format=xlsx")
    check("xlsx 200", resp.status_code == 200)
    check("xlsx filename", resp.headers["Content-Disposition"].endswith('attendance_2026-10.xlsx'))
    from openpyxl import load_workbook
    wb = load_workbook(io.BytesIO(resp.data))
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    check("xlsx headers", list(rows[0]) == app_module.EXPORT_HEADERS)
    check("xlsx 3 data rows", len(rows) == 4)
    check("xlsx date stored as plain text", isinstance(rows[1][4], str) and rows[1][4] == "2026-10-01")
    check("xlsx hours numeric", isinstance(rows[1][6], (int, float)) and rows[1][6] == 7.5)
    check("xlsx header styled bold", ws["A1"].font.bold is True)

    # empty month ---------------------------------------------------------
    resp = client.get("/export/download?month=1&year=2026&format=csv", follow_redirects=True)
    check("empty month redirects with message", b"No attendance records for January 2026" in resp.data)

    # JSON import ---------------------------------------------------------
    sample = {
        "employees": [
            {"id": "emp_002", "name": "Sara Ahmed", "department": "HR"},
            {"name": "New Guy", "designation": "Operator"},
        ],
        "attendance": {
            "emp_002": {"2026-10-05": {"arrival": "22:15", "hours": 8}},
            "emp_999": {"2026-10-05": {"arrival": "09:00", "hours": 8}},
        },
    }
    resp = client.post("/import", data={
        "file": (io.BytesIO(json.dumps(sample).encode()), "sample.json"),
    }, content_type="multipart/form-data", follow_redirects=True)
    body = resp.data.decode("utf-8")
    check("import summary", "1 employee(s) added, 1 updated, 1 attendance record(s) added, 0 updated." in body, body[:400])
    check("import skips unknown emp", "unknown employee: emp_999" in body)
    check("import derived Late status", client.get("/api/attendance?emp_id=emp_002&date=2026-10-05").get_json()["record"]["status"] == "Late")
    resp = client.post("/import", data={
        "file": (io.BytesIO(b"not json at all"), "bad.json"),
    }, content_type="multipart/form-data", follow_redirects=True)
    check("bad json rejected", b"Could not parse" in resp.data)

    # toggle / delete -----------------------------------------------------
    resp = client.post("/employees/emp_002/toggle", follow_redirects=True)
    check("mark ex", b"ex-employee" in resp.data)
    check("ex flag stored", [e for e in json.loads((tmp / "employees.json").read_text("utf-8"))["employees"] if e["id"] == "emp_002"][0]["active"] is False)
    resp = client.post("/employees/emp_002/toggle", follow_redirects=True)
    check("mark active again", b"ACTIVE" in resp.data)
    resp = client.post("/employees/emp_002/delete", follow_redirects=True)
    check("delete employee + its attendance", b"Deleted emp_002 and 1 attendance record(s)" in resp.data)
    check("attendance for emp_002 gone", "emp_002" not in json.loads((tmp / "attendance.json").read_text("utf-8"))["records"])
    check("emp_001 attendance kept", "emp_001" in json.loads((tmp / "attendance.json").read_text("utf-8"))["records"])

    # report --------------------------------------------------------------
    failed = [r for r in results if not r[1]]
    for name, ok, extra in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  <- {extra}" if not ok else ""))
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
