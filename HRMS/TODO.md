# TODO.md - HRMS

## Done (working)

- [x] Flask app, no login, data stored in JSON files (`data/*.json`), run = update = close
- [x] Employees: add / edit / delete, auto ID `emp_001`, optional department + designation + join date (`added_on`)
- [x] `Mark ex` soft-delete keeps attendance history; `Delete` removes employee + records (confirmed)
- [x] Manual attendance entry: employee + date (defaults today) + day type (Worked / Approved leave / Absent) + arrival time + hours
- [x] Office timing `LATE_TIME = 22:00` + `OFFICE_END = 05:00` (nights 10 PM -> 5 AM) -> after 22:00 up to 05:00 = `Late` - both editable from the web on the Settings page
- [x] Re-opening an existing date shows an orange "already has data" warning, prefills it, saving updates
- [x] Automatic status: Present / Late for worked days; explicit Absent / Approved leave (`Leave`)
- [x] **Unmarked day = Absent**: opening the Export page saves Absent records for unmarked working days (past days only, never overwrites your marks) - so the sheet is always complete
- [x] Off days never auto-filled: `OFF_DAYS`, default `["Saturday"]` - tick/untick days on the Settings page (all 7 days listed)
- [x] Ex employees: auto-absent only up to their last marked day of the month; not-yet-joined employees untouched
- [x] Export by month + year: CSV and XLSX downloads (empty month = message, no empty file)
- [x] Google Sheets friendly: UTF-8 BOM CSV; XLSX with plain YYYY-MM-DD text dates, styled header, colour-coded status (incl. blue Leave), frozen header + filter
- [x] JSON file import: bulk add/update employees and attendance, skips + reports invalid entries
- [x] **Transactions page**: image + name + date + amount + client (optional); images saved locally in `data/uploads/` as `txn_001.png` (PNG/JPG/WEBP/GIF, max 8 MB, server-generated names)
- [x] Transaction **search**: month + year filter with summary cards (transactions / total amount / **people count**) and **complete per-person history** (name filter, case-insensitive), delete removes record + image
- [x] **Totals dashboard**: KPI cards (all-time amount, this month, people, count), last-12-months bar chart, top-people donut (SVG), recent transactions, empty state
- [x] **Theme**: dark-green direction applied to every page (palette `#9FDC56` / `#EAFFD2` / `#FF7366` / `#545FFF` / `#161815`, pill nav, "HRMS" brand, Neue Montreal fallback)
- [x] **Calendar view**: month grid (Monday first) - each day cell shows the day's **total transactions (all names)** + **attendance %** (colour-coded, ratio in tooltip); beside the month name: **month attendance %** + **month total** (+ txns count); Prev/Next + jump-to-month, off days dashed, today highlighted, empty months show "—"
- [x] **Day detail** (`/calendar/<date>`, click a calendar day): complete attendance table for the day (status badge / arrival / hours) + **Transactions column per person** (count + amount) + **Day total row** over all transactions (names outside the employee list noted below); off-day/future banners, prev/next-day links
- [x] **Status editing from the day table**: top-right toggle turns the badges into click-to-cycle (`Present -> Late -> Absent -> Leave`, unmarked `-` becomes `Present`), saved instantly via `POST /api/attendance/status` (no page reload)
- [x] `start.bat` - double-click to run the app in a shell window
- [x] `smoke_test.py` - 120 end-to-end checks, all passing (incl. uploads, traversal guard, dashboard KPIs, calendar math, edit/settings/day detail, night-shift status, status cycling)
- [x] Docs: `README.md` (user guide **with mermaid diagrams** + **screenshots from `snap/`**), `AGENTS.md` (agents), this file

## Later / if wanted (not built yet - do not build without asking)

- [ ] Transactions: CSV/XLSX export of a month (like attendance), edit-in-place instead of
      delete + re-add, multiple images per record, currency symbol/setting
- [ ] **Full-detail attendance record**: fields `check_in`, `check_out`, `note` added to each
      record next to `arrival` / `hours` / `status`; extra export columns appear only when
      requested. (Planned per user, storage already easy to extend.)
- [ ] Export polish: per-employee summary block (present/late/absent totals + total hours),
      department column filter, logo/title row
- [ ] Employees page: quick CSV/XLSX download of the employee list
- [ ] Attendance page: month grid/list view showing existing marks at a glance
- [ ] Dashboard: date-range picker (not just all-time / this month / 12-month bars)
- [ ] Day view: edit arrival/hours or add a transaction directly from the day detail
      page (status cycling is done); optional Sunday-first calendar weeks
- [ ] Link transactions to employees/clients registry (currently free-text names by design)
- [ ] Multi-user/network use -> then, and only then, add simple auth (user said: no login for now)
