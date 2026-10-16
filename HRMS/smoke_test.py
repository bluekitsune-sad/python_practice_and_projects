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
    def save(day: str, arrival: str, hours: str, day_type: str = "worked") -> str:
        data = {
            "emp_id": "emp_001", "day": day, "arrival": arrival,
            "hours": hours, "day_type": day_type,
        }
        return client.post("/attendance", data=data, follow_redirects=True).data.decode("utf-8")

    out = save("2026-10-01", "09:00", "8")
    check("on-time -> Present", "Saved emp_001 on 2026-10-01: Present." in out)
    out = save("2026-10-02", "22:30", "8")
    check("after 22:00 -> Late", "Late" in out)
    out = save("2026-10-03", "", "0", "absent")
    check("absent saved", "Absent" in out)
    out = save("2026-09-15", "", "0", "leave")
    check("approved leave saved", "Saved emp_001 on 2026-09-15: Leave." in out)
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

    # leave export (September, separate from the October baseline) ---------
    resp = client.get("/export/download?month=9&year=2026&format=csv")
    text_sep = resp.data.decode("utf-8-sig")
    check("september export has Leave row", "2026-09-15,Leave,0.0" in text_sep.replace('"', ""))
    check("september export row count", len(text_sep.splitlines()) == 2, str(len(text_sep.splitlines())))

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
            "emp_002": {
                "2026-10-05": {"arrival": "22:15", "hours": 8},
                "2026-10-06": {"arrival": "", "hours": 0, "status": "Leave"},
            },
            "emp_999": {"2026-10-05": {"arrival": "09:00", "hours": 8}},
        },
    }
    resp = client.post("/import", data={
        "file": (io.BytesIO(json.dumps(sample).encode()), "sample.json"),
    }, content_type="multipart/form-data", follow_redirects=True)
    body = resp.data.decode("utf-8")
    check("import summary", "1 employee(s) added, 1 updated, 2 attendance record(s) added, 0 updated." in body, body[:400])
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
    check("delete employee + its attendance", b"Deleted emp_002 and 2 attendance record(s)" in resp.data)
    check("attendance for emp_002 gone", "emp_002" not in json.loads((tmp / "attendance.json").read_text("utf-8"))["records"])
    check("emp_001 attendance kept", "emp_001" in json.loads((tmp / "attendance.json").read_text("utf-8"))["records"])

    # default absent fill: unmarked working day -> saved Absent -------------
    # Pin "today" so expectations never change with the real date.
    from datetime import date as _RealDate

    class _FixedDate(_RealDate):
        @classmethod
        def today(cls):
            return cls(2026, 10, 16)  # a Friday

    app_module.date = _FixedDate

    emps_doc = json.loads((tmp / "employees.json").read_text("utf-8"))
    for emp in emps_doc["employees"]:
        # emp_001 joined at the start of Oct; everyone else much later (no fill)
        emp["added_on"] = "2026-10-01" if emp["id"] == "emp_001" else "2099-12-31"
    (tmp / "employees.json").write_text(json.dumps(emps_doc), encoding="utf-8")

    resp = client.get("/export?month=10&year=2026")
    body = resp.data.decode("utf-8")
    check("export page fills unmarked days", "Auto-filled 12" in body, body[:300])

    att = json.loads((tmp / "attendance.json").read_text("utf-8"))["records"]
    # Oct 1..16 minus Saturdays (3rd, 10th) minus the 3 already-marked days
    expected_fill = {
        f"2026-10-{day:02d}" for day in (4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16)
    }
    filled = {
        k for k, v in att["emp_001"].items()
        if v["status"] == "Absent" and k != "2026-10-03"
    }
    check("fill covers exactly the unmarked working days", filled == expected_fill,
          f"extra={sorted(filled - expected_fill)} missing={sorted(expected_fill - filled)}")
    check("Saturdays are never auto-filled", "2026-10-10" not in att["emp_001"])
    check("existing marks never overwritten",
          att["emp_001"]["2026-10-01"]["status"] == "Present"
          and att["emp_001"]["2026-10-01"]["hours"] == 7.5)
    check("not-yet-joined employee not filled", "emp_003" not in att)
    check("filled record shape",
          att["emp_001"]["2026-10-16"] == {"arrival": "", "hours": 0.0, "status": "Absent"},
          str(att["emp_001"].get("2026-10-16")))

    # ex employee: fill only up to their last marked day of the month -------
    ex_sample = {
        "employees": [{"id": "emp_004", "name": "Ex Guy", "active": False,
                       "added_on": "2026-10-01"}],
        "attendance": {"emp_004": {"2026-10-05": {"arrival": "09:00", "hours": 8,
                                                  "status": "Present"}}},
    }
    resp = client.post("/import", data={
        "file": (io.BytesIO(json.dumps(ex_sample).encode()), "ex.json"),
    }, content_type="multipart/form-data", follow_redirects=True)
    check("ex employee imported", "1 employee(s) added, 0 updated" in resp.data.decode("utf-8"))

    resp = client.get("/export?month=10&year=2026")
    check("second fill pass = only ex-employee days", "Auto-filled 3" in resp.data.decode("utf-8"))
    att = json.loads((tmp / "attendance.json").read_text("utf-8"))["records"]
    check("ex employee filled only up to last mark",
          set(att["emp_004"]) == {"2026-10-01", "2026-10-02", "2026-10-04", "2026-10-05"},
          str(sorted(att["emp_004"])))

    # auto-absent can be corrected to approved leave ------------------------
    out = save("2026-10-04", "", "0", "leave")
    check("auto-absent day can be changed to approved leave", "2026-10-04: Leave" in out)

    resp = client.get("/export/download?month=10&year=2026&format=csv")
    text = resp.data.decode("utf-8-sig")
    lines = [ln for ln in text.splitlines() if ln]
    # header + emp_001 (15 Oct days) + emp_004 (4 days); emp_003 has none
    check("final csv row count", len(lines) == 20, str(len(lines)))
    check("final csv has Leave row", ",2026-10-04,Leave,0.0" in text.replace('"', ""))
    check("final csv has auto Absent rows", ",2026-10-16,Absent,0.0" in text.replace('"', ""))

    resp = client.get("/export/download?month=10&year=2026&format=xlsx")
    wb2 = load_workbook(io.BytesIO(resp.data))
    rows2 = list(wb2.active.iter_rows(values_only=True))
    check("final xlsx row count", len(rows2) == 20, str(len(rows2)))
    leave_cells = [r for r in wb2.active.iter_rows(min_row=2) if r[5].value == "Leave"]
    check("xlsx Leave row colour", leave_cells and leave_cells[0][5].fill.fgColor.rgb.endswith("DDEBF7"))

    # transactions ---------------------------------------------------------
    resp = client.get("/transactions")
    check("GET /transactions -> 200", resp.status_code == 200)
    png = b"\x89PNG\r\n\x1a\n" + b"fake-png-bytes" * 4

    def add_txn(name, day, amount, client_name="", fname="receipt.png"):
        return client.post("/transactions", data={
            "name": name, "day": day, "amount": amount, "client": client_name,
            "image": (io.BytesIO(png), fname),
        }, content_type="multipart/form-data", follow_redirects=True).data.decode("utf-8")

    body = add_txn("Client A", "2026-10-14", "1500.5")
    check("add transaction saves record + image",
          "Added txn_001" in body and (tmp / "uploads" / "txn_001.png").exists(), body[:200])
    check("add transaction stored in JSON",
          any(t["id"] == "txn_001" and t["amount"] == 1500.5 and t["client"] == ""
              for t in json.loads((tmp / "transactions.json").read_text("utf-8"))["transactions"]))
    check("second transaction (other month, with client)",
          "Added txn_002" in add_txn("Client B", "2026-09-20", "499.5", client_name="Acme"))
    check("third transaction", "Added txn_003" in add_txn("Client C", "2026-10-15", "49.5"))

    out = client.post("/transactions", data={"name": "X", "day": "2026-10-01", "amount": "5"},
                      follow_redirects=True).data.decode("utf-8")
    check("transaction without image rejected", "An image is required" in out)
    out = add_txn("X", "2026-10-01", "5", fname="evil.exe")
    check("bad image extension rejected",
          "Image must be one of" in out and not (tmp / "uploads" / "txn_004.exe").exists())
    out = client.post("/transactions", data={"name": "X", "day": "2026-10-01", "amount": "-5",
                                             "image": (io.BytesIO(png), "ok.png")},
                      content_type="multipart/form-data", follow_redirects=True).data.decode("utf-8")
    check("negative amount rejected", "Amount must be a positive number" in out)
    check("fourth transaction", "Added txn_004" in add_txn("Client A", "2026-08-30", "200"))

    # monthly search: 2 txns in Oct (Client A + C), 1,550.00, 2 people
    body = client.get("/transactions?month=10&year=2026").data.decode("utf-8")
    check("month search Oct: count/amount/people",
          'id="sum-count">2<' in body and "1,550.00" in body and 'id="sum-people">2<' in body,
          body[:0] or "summary mismatch")
    body = client.get("/transactions?month=9&year=2026").data.decode("utf-8")
    check("month search Sep: single record",
          'id="sum-count">1<' in body and "499.50" in body and 'id="sum-people">1<' in body)

    # individual complete history: Client A = txn_001 (Oct) + txn_004 (Aug)
    body = client.get("/transactions?name=Client%20A").data.decode("utf-8")
    check("individual history: 2 records, 1,700.50",
          "Complete history" in body and 'id="sum-count">2<' in body and "1,700.50" in body,
          "history mismatch")

    # delete removes record + image
    resp = client.post("/transactions/txn_002/delete", follow_redirects=True)
    check("delete transaction + image",
          b"Deleted txn_002" in resp.data and not (tmp / "uploads" / "txn_002.png").exists())
    remaining = [t["id"] for t in json.loads((tmp / "transactions.json").read_text("utf-8"))["transactions"]]
    check("json after delete", remaining == ["txn_001", "txn_003", "txn_004"], str(remaining))

    # image serving + safety
    resp = client.get("/uploads/txn_001.png")
    check("image served over HTTP", resp.status_code == 200 and resp.data.startswith(b"\x89PNG"))
    check("upload path traversal blocked",
          client.get("/uploads/..%2femployees.json").status_code == 404)

    # totals dashboard -----------------------------------------------------
    resp = client.get("/dashboard")
    body = resp.data.decode("utf-8")
    check("GET /dashboard -> 200", resp.status_code == 200)
    # remaining: 1500.5 + 49.5 + 200 = 1,750.00 across 3 records, 2 people (A, C)
    check("dashboard KPIs (total/count/people)",
          'id="kpi-total">1,750.00<' in body and 'id="kpi-count">3<' in body
          and 'id="kpi-people">2<' in body, "KPI mismatch")
    check("dashboard this-month KPI (pinned Oct)", 'id="kpi-month">1,550.00<' in body)
    check("dashboard has bar chart + donut + recent",
          'class="bars"' in body and "<svg" in body and "Recent transactions" in body)

    body = client.get("/").data.decode("utf-8")
    check("home shows transaction stat", "Transactions · 1,750.00" in body)

    # calendar view --------------------------------------------------------
    resp = client.get("/calendar?month=10&year=2026")
    body = resp.data.decode("utf-8")
    check("GET /calendar -> 200", resp.status_code == 200)
    # attendance: 3 attended / 18 expected = 16.7%; transactions: 1500.5 + 49.5
    check("calendar month chips: attendance % + month total",
          'id="cal-att">16.7%<' in body and 'id="cal-total">1,550.00<' in body)
    check("day cell shows attendance ratio", "Attendance 1/2" in body)
    check("day cell shows transaction total", "1,500.50" in body)
    check("off day (Saturday) styled", "cal-cell off" in body)
    check("prev/next month links",
          "month=9&amp;year=2026" in body and "month=11&amp;year=2026" in body)
    resp = client.get("/calendar?month=1&year=2025")
    body = resp.data.decode("utf-8")
    check("empty month chips (dash + zero)",
          'id="cal-att">—<' in body and 'id="cal-total">0.00<' in body)

    # report --------------------------------------------------------------
    failed = [r for r in results if not r[1]]
    for name, ok, extra in results:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  <- {extra}" if not ok else ""))
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    shutil.rmtree(tmp, ignore_errors=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
