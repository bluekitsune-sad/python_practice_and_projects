# AGENTS.md - instructions for agents working in this folder

Scope: **only** the `HRMS/` folder. This is a deliberately small local tool - do not
over-scope it (no login, no database, no frameworks beyond Flask + openpyxl).

## What this project is

Flask app (`app.py`, ~1 file) for one person to manage employees + attendance, keep
transaction records with receipt images, and export a month of attendance as CSV/XLSX that
must open cleanly in Google Sheets (manual acceptance test). Includes a Totals dashboard.

## Layout

```
HRMS/
  app.py            all routes, JSON storage, CSV/XLSX builders, dashboard math
  smoke_test.py     end-to-end checks (python smoke_test.py) - temp data dir, never real data
  start.bat         Windows launcher: opens a shell and runs python app.py (keeps it open)
  requirements.txt  flask, openpyxl
  templates/        base.html (layout + theme CSS) + index/employees/employee_edit/
                    attendance/settings/transactions/calendar/day/dashboard/export/import
  data/             JSON source of truth: config.json, employees.json, attendance.json,
                    transactions.json   +  data/uploads/ (transaction images) - all local-only
  snap/             app screenshots (1..7.PNG) embedded in README - UI only, never user data
  README.md         user-facing docs (incl. mermaid diagrams)  |  TODO.md: status + future
```

## Conventions (keep these)

- **Storage**: `data/*.json`, loaded/saved through `_load` / `_save` (atomic tmp+replace,
  indent 2). Reads use `utf-8-sig` (BOM-proof) - a BOM'd file must never look like empty
  data, or the next save would wipe user records. Shapes:
  `employees.json = {"employees": [...]}`,
  `attendance.json = {"records": {emp_id: {date: record}}}`,
  `transactions.json = {"transactions": [{id, name, date, amount, client, image}]}`.
- **Transaction IDs / images**: `txn_001` style via `next_transaction_id()`; images stored
  as `txn_001.png` in `upload_dir()` (= `data/uploads/`, follows DATA_DIR so tests stay
  isolated). Never use the client's filename; whitelist `UPLOAD_EXTS`, cap 8 MB via
  `MAX_CONTENT_LENGTH`. Serving via `/uploads/<filename>` + `send_from_directory` only.
- **Settings**: `LATE_TIME` (office start, default `22:00`), `OFFICE_END` (default `05:00`)
  and `OFF_DAYS` (default `["Saturday"]`, English weekday names) live in `data/config.json`,
  read via `load_config()`. Never hardcode them elsewhere. They are edited from the web on
  the **Settings** page (`/settings`, `settings_page`): times validated/normalised by
  `normalize_time()` (HH:MM, 00:00-23:59), off days built from the `WEEKDAYS` constant,
  saved through `_save` so the file stays atomic and keeps any other keys.
- **Employee edit**: `/employees/<id>/edit` (`employee_edit`) changes name / department /
  designation / `added_on` only - the `emp_001` id never changes. Re-render the form (no
  redirect) on validation errors so typed values survive; `Mark ex` / `Delete` stay on the
  list page.
- **Day detail** (`/calendar/<YYYY-MM-DD>`, `day_page`): one day - complete attendance table
  (status badges, arrival, hours) plus transactions. The per-row *Transactions* cell matches
  records to the employee by **case-insensitive exact name**; the footer total always covers
  EVERY transaction of that day, and names not in the employee list are noted under the
  table. Runs `materialize_absents` first (same fill rule as calendar/export), shows off-day
  and future-date banners, and offers prev-day / month-view / next-day links.
- **Status cycling** (day table): the `#status-toggle` button switches the table into
  click-to-cycle mode (vanilla JS, no library). Clicking a badge POSTs JSON to
  `/api/attendance/status` (`api_set_status`: validates status against `STATUSES` -> 400,
  date -> 400, employee -> 404) and cycles `Present -> Late -> Absent -> Leave`; an unmarked
  `—` creates a Present record. Absent/Leave clear arrival + hours (same as the form).
  Keep it a toggle - never auto-edit data from a page load.
- **Statuses**: only `Present`, `Late`, `Absent`, `Leave` (`STATUSES`); `Leave` = approved
  leave, marked manually via the attendance form's day-type select. Worked-day statuses are
  derived from the office window (`attendance_status`, see below) unless explicitly given
  (import).
- **Office timing (night shift)**: the office runs **22:00 -> 05:00**, so
  `attendance_status(arrival, late_time, office_end)` returns Late when arrival is after
  `LATE_TIME`, **and** - when the shift wraps midnight (`LATE_TIME` > `OFFICE_END`) - also
  for any arrival up to and including `OFFICE_END`. Example with 22:00-05:00: 22:30 /
  02:30 / 05:00 = Late, 21:30 / 06:00 = Present. Day shifts (`start < end`) keep the simple
  "after start = Late" rule.
- **Auto-absent fill**: `materialize_absents(year, month)` WRITES saved Absent records for
  unmarked working days - called from the export PAGE and the calendar PAGE (both report
  attendance, so both must materialize first); downloads never fill. Rules: past days only,
  OFF_DAYS skipped, never overwrites, active from `max(1st, added_on)`, ex employees only up
  to their last marked day of the month. Extend tests when touching it.
- **Attendance % formula** (calendar day cells + month chip): attended = `Present` + `Late`;
  expected = every non-`Leave` record that day; `Leave` is excused (counted on neither
  side); `Absent` counts as expected but not attended; no records -> show `—`. Month % =
  sum over the month. Keep this consistent everywhere attendance % is shown.
- **IDs**: `emp_001` / `txn_001` style, never reused, generated by the `next_*_id()` helpers.
- **Soft delete**: leavers are `active: false` (ex) so history survives; hard delete must
  also remove that employee's attendance (see `employee_delete`); deleting a transaction
  must also unlink its image (see `transaction_delete`).
- **Export rules**: CSV must stay `utf-8-sig` + csv module defaults; XLSX dates stay plain
  `YYYY-MM-DD` strings (never datetime cells) or Google Sheets mis-displays them. Columns
  are fixed in `EXPORT_HEADERS`. Every status needs an XLSX colour + a `.badge.*` CSS class.
- **Charts**: dashboard graphs are hand-built (CSS bars + inline SVG donut) - no chart
  library, no CDN/internet dependency. Keep it that way.
- **Theme** (from the user's design direction): dark-green palette, defined as CSS vars in
  `base.html` - accent `#9FDC56`, pale text `#EAFFD2`, coral `#FF7366`, blue `#545FFF`,
  base `#161815`. Neue Montreal font with system fallback. New UI must reuse these vars
  (buttons, badges, cards) instead of introducing new colours; amber `#E9C46A` exists only
  for the "already has data" warning.
- **No auth**: app binds `127.0.0.1` only. Never add a login page or expose it to a network.
- Flash messages for user feedback; forms are plain POST + redirect (no JS frameworks).
- **User data never goes to GitHub**: `data/employees.json`, `attendance.json`,
  `transactions.json` and `data/uploads/` are git-ignored - don't un-ignore them.

## Before finishing a change

1. Run `python smoke_test.py` - must stay 120/120 (extend it when you add behaviour).
2. Check `http://127.0.0.1:5000` renders (python app.py, or start.bat on Windows).
3. Update `README.md` and `TODO.md` so docs match reality.
4. The JSON files are user data - never rewrite their schema without a migration note.

## Planned-for-later (documented, not built)

- Full-detail attendance: add `check_in`, `check_out`, `note` fields to each record
  alongside the current `arrival`/`hours`/`status`; export gains columns only when asked.
- Transactions: CSV/XLSX export, edit-in-place, multiple images per record.
- See `TODO.md` for the rest.
