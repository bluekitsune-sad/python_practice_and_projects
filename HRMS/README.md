# HRMS

A small local HRMS: employees, attendance and monthly CSV/XLSX exports.
No login, no database - all data lives in plain JSON files.

## Install & run

```bash
pip install -r requirements.txt
python app.py
```

Or on Windows just double-click **`start.bat`** - it opens a shell, runs the app and keeps
the window open (close it when you are done).

Open http://127.0.0.1:5000 , make your changes, close the browser (and the app when done).
The data files in `data/` are your permanent record - back them up.

## Pages

| Page | What it does |
|------|--------------|
| **Home** | Counts + quick start. |
| **Employees** | Add employees (ID `emp_001`, `emp_002`... auto-generated). Department and designation are optional. `Mark ex` keeps the person out of active use but preserves all history; `Delete` removes the person **and** their attendance records (there is a confirmation prompt). |
| **Attendance** | Pick employee + date (defaults to today) and a **day type**: *Worked* (enter arrival time + hours; status is automatic - **Present** at/before the late time, **Late** after), *Approved leave*, or *Absent*. Going back to a date that already has data shows an orange warning and prefills it; saving again updates it. |
| **Export** | Choose month + year, then download CSV or XLSX. Opening this page also **saves** the auto-absents (see below), so the file and the data always match. |
| **Import JSON** | Upload a correctly formatted `.json` file to bulk add/update employees and attendance. Nothing is ever deleted by an import. |

## Unmarked day = Absent (automatic)

When you open the **Export** page for a month, every **working day** you have not marked is
filled with a saved `Absent` record - so nobody can be missed just because you forgot a day.

- **Past days only** - future/current days are never guessed.
- **Off days are skipped** - default `["Saturday"]`, edit `OFF_DAYS` in `data/config.json`
  (e.g. `["Saturday", "Sunday"]`).
- **Records you already marked are never overwritten** - to excuse a day, change it to
  *Approved leave* on the Attendance page (an auto-Absent can be corrected afterwards).
- **Ex employees**: only filled up to the last day they were marked in that month.
- **Not-yet-joined employees** (`added_on` is later) are not touched.

## The settings constants

`data/config.json`:

```json
{ "LATE_TIME": "22:00", "OFF_DAYS": ["Saturday"] }
```

- `LATE_TIME` - arrival after this time (24h clock) = status `Late`.
- `OFF_DAYS` - weekday names (English, as in `strftime("%A")`) never auto-marked absent.

## Export files (tested against Google Sheets)

- Columns: `Employee ID, Name, Department, Designation, Date, Status, Hours` - one row per
  attendance record of the selected month, sorted by date then employee.
- Statuses: `Present`, `Late`, `Absent`, `Leave` (approved leave).
- **CSV**: UTF-8 **with BOM**, comma separated, CRLF lines - Google Sheets and Excel detect
  the encoding correctly, so names with accents or commas don't get garbled.
- **XLSX**: bold dark-blue header, frozen header row, auto-filter, sensible column widths,
  colour-coded Status (green Present / yellow Late / red Absent / blue Leave). Dates are
  stored as plain `YYYY-MM-DD` text so Google Sheets never turns them into serial numbers.
- Empty month = no file, a message instead.
- To view on Google Drive: upload → right-click → **Open with > Google Sheets**.

## Data files (JSON source of truth)

`data/employees.json`

```json
{ "employees": [ { "id": "emp_001", "name": "Ali Khan", "department": "Operations",
                   "designation": "Supervisor", "active": true, "added_on": "2026-10-16" } ] }
```

`data/attendance.json` - keyed by employee, then by `YYYY-MM-DD`:

```json
{ "records": { "emp_001": { "2026-10-01": { "arrival": "09:00", "hours": 8, "status": "Present" } } } }
```

### Import file format

Both keys optional; existing ids/dates are updated, new ones added, missing fields default:

```json
{
  "employees": [
    { "id": "emp_001", "name": "Ali Khan", "department": "Operations",
      "designation": "Supervisor", "active": true }
  ],
  "attendance": {
    "emp_001": {
      "2026-10-01": { "arrival": "09:00", "hours": 8, "status": "Present" },
      "2026-10-02": { "arrival": "22:30", "hours": 8, "status": "Late" },
      "2026-10-03": { "arrival": "",      "hours": 0, "status": "Absent" },
      "2026-10-06": { "arrival": "",      "hours": 0, "status": "Leave" }
    }
  }
}
```

Rules: an employee without an `id` gets the next free one; an invalid/missing `status` is
recomputed from `arrival` vs `LATE_TIME`; `status` must be Present, Late, Absent or Leave;
unknown employee ids are skipped and reported.

## Tests

```bash
python smoke_test.py
```

61 end-to-end checks against a temporary data folder (your real data is not touched).

## Not included (on purpose)

No login (local single-user tool), no network deployment hardening, no payrolls/reports
beyond the monthly export. See `TODO.md` for the agreed future items.
