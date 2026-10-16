# HRMS

A small local HRMS: employees, attendance, **transactions with receipt images** and
monthly CSV/XLSX exports, plus a **Totals dashboard** with graphs.
No login, no database - all data lives in plain JSON files (images on disk).

## Install & run

```bash
pip install -r requirements.txt
python app.py
```

Or on Windows just double-click **`start.bat`** - it opens a shell, runs the app and keeps
the window open (close it when you are done).

Open http://127.0.0.1:5000 , make your changes, close the browser (and the app when done).
The `data/` folder is your permanent record - back it up.

## How it fits together

```mermaid
flowchart LR
    B["Browser (no login)"] --> A["Flask app.py"]
    A --> E["data/employees.json"]
    A --> AT["data/attendance.json"]
    A --> T["data/transactions.json"]
    A --> U["data/uploads/ (receipt images)"]
    A --> C["Download: CSV (utf-8-sig) / XLSX"]
    CFG["data/config.json<br/>LATE_TIME, OFF_DAYS"] -.-> A
```

## Pages

| Page | What it does |
|------|--------------|
| **Home** | Counts (employees, attendance, transactions) + quick start. |
| **Employees** | Add employees (ID `emp_001`, `emp_002`... auto-generated). Department and designation are optional. **Edit** fixes the name / department / designation / join date (the ID never changes). `Mark ex` keeps the person out of active use but preserves all history; `Delete` removes the person **and** their attendance records (confirmation prompt). |
| **Attendance** | Pick employee + date (defaults to today) and a **day type**: *Worked* (enter arrival time + hours; status is automatic - **Present** if you arrive by the office start, **Late** after it, including the early-morning hours up to the office end), *Approved leave*, or *Absent*. Re-opening a date that has data shows an orange warning and prefills it. |
| **Transactions** | Save an **image/receipt + name + date + amount + client (optional)**. Search by **month + year** (see count, total amount and **how many people** transacted that month) or by **person for their complete history**. Delete removes the record and its image. |
| **Calendar** | Month grid: every day cell shows that day's **total transactions (all names)** and **attendance %**; beside the month name sit the **month's attendance %** and **month total**. Prev/Next navigation, off days dashed, today highlighted. **Click any day** to open its detail page. |
| **Day detail** | `/calendar/<date>` - that day's **complete attendance in a table** (ID, name, department, status badge, arrival, hours) with a **Transactions column** (count + amount per person) and a **Day total row** for all transactions. A **Status editing** button (top-right) lets you click any status to cycle it `Present → Late → Absent → Leave` - saved instantly. Prev-day / month / next-day links; off-day and future-date banners. |
| **Totals** | Dashboard: KPI cards (all-time amount, this month, people, count), a **bar chart** of the last 12 months, a **donut** of top people by amount and the recent transactions. |
| **Export** | Choose month + year, download the attendance CSV or XLSX. Opening this page also **saves** the auto-absents (see below). |
| **Import** | Upload a correctly formatted `.json` file to bulk add/update employees and attendance. Nothing is ever deleted by an import. |
| **Settings** | The **office timing** - start (`LATE_TIME`) and end (`OFFICE_END`, next morning) - plus the `OFF_DAYS` checkboxes. Saved to `data/config.json`, no file editing needed; invalid times are rejected. |

## Transactions

```mermaid
flowchart TD
    F["Add form<br/>image + name + date + amount + client?"] --> S["Image saved as<br/>data/uploads/txn_001.png"]
    F --> R["Record saved in<br/>data/transactions.json"]
    R --> Q{"Search filters<br/>(month + year + name)"}
    Q --> M["Monthly view:<br/>count + total amount + people"]
    Q --> H["Individual complete history<br/>+ that person's total"]
    R --> D["Totals dashboard:<br/>KPIs + bar chart + donut"]
```

Rules:

- **Image** is required; PNG / JPG / WEBP / GIF up to **8 MB**. The file is stored under a
  server-generated name (`txn_001.png`), never the original filename.
- **Client** is optional. Amount must be a positive number (no currency symbol is stored -
  the value is shown with thousand separators).
- Search filters combine: `month` + `year` + `name` (name is a case-insensitive substring).
  The summary cards always show **Transactions / Total amount / People** for the current
  search - "People" is the distinct number of names, so a month's card answers
  *"how many people transacted this month"*.
- Typing a person's name shows their **complete history** (all months) with their total;
  add a month filter to narrow it.
- `Delete` removes the JSON record **and** the image file (with confirmation).

## Totals dashboard

- **KPIs**: total amount (all time), this month's amount (+ how many transactions and
  people), distinct people / clients, transaction count.
- **Bar chart**: amounts per month for the last 12 months, current month highlighted.
- **Donut**: top 5 people by amount (+ "Others"), with percentages and amounts.
- **Recent**: the 5 newest transactions with thumbnails.
- Charts are hand-built (CSS bars + inline SVG) - no chart library, no internet needed.
- Empty state guides you to the Transactions page.

## Calendar view

A month grid (Monday-first) that combines both worlds at a glance:

- **Beside the month name**: two chips - **Attendance this month %** and
  **Total this month** (with the transaction count under it).
- **Every day cell**: the day's **total transaction amount** (all names together, with the
  count) and the day's **attendance %**, colour-coded: lime 90%+, pale 70-89%, coral below
  70%, `—` when nobody has records that day. Hover a cell for the exact ratio
  (e.g. `Attendance 6/7 - 2 transaction(s), 1,500.50`).
- Off days are dashed/muted, today's number is a lime disc, `‹ Prev` / `Next ›` walk the
  months, and a jump form goes to any month/year.

**Attendance % formula** (same everywhere): attended = `Present` + `Late`; expected = every
record that isn't `Leave` (approved leave is excused - counted on neither side); `Absent`
counts as expected but not attended.

Opening a month on the calendar runs the same *unmarked = Absent* fill as the Export page,
so the percentages always reflect reality.

### Clicking a day

Every day cell links to `/calendar/<YYYY-MM-DD>` - the **day detail** page:

- Chips for the day: **transaction count** and **total amount**.
- The **complete attendance table** for that day: ID, name, department, status badge
  (`Present` / `Late` / `Absent` / `Leave`), arrival and hours. Active employees with no
  record show `—`; ex employees only appear when they actually have something that day;
  people who had not joined yet are left out.
- A **Transactions column per person** (`2 txns · 1,500.50`) - records are matched to the
  employee by case-insensitive exact name - plus a **Day total row** that sums *every*
  transaction of the day. Transactions recorded under a name that isn't in the employee
  list are listed below the table (still included in the day total).
- Off-day and future-date banners, and `‹ prev day` / `Month view` / `next day ›` links.
- Opening a day runs the same auto-absent fill for that month first.
- **Status editing**: click the **Status editing** button at the top-right of the table,
  then click any status badge to cycle it (`Present → Late → Absent → Leave → ...`) -
  each click saves instantly (no page reload). An unmarked `—` becomes a `Present` record.
  `Absent` / `Leave` clear the arrival + hours, exactly like the attendance form.

## Attendance: unmarked day = Absent (automatic)

When you open the **Export** or **Calendar** page for a month (or any **day page**), every
**working day** you have not marked is filled with a saved `Absent` record - so nobody can
be missed just because you forgot a day.

```mermaid
flowchart TD
    U["Open a month on Export/Calendar or any day page"] --> F["materialize_absents()"]
    F --> Q{"day already marked?"}
    Q -->|"yes"| KEEP["never overwritten<br/>change it to Approved leave if needed"]
    Q -->|"no"| W{"working day AND in the past?"}
    W -->|"off day / future day"| SK["skip - nothing saved"]
    W -->|"working day, past"| AB["save Absent record"]
    KEEP --> R["Rows built from attendance.json"]
    AB --> R
    R --> X["CSV (utf-8-sig) or XLSX download"]
```

- **Past days only** - future/current days are never guessed.
- **Off days are skipped** - default `["Saturday"]`, change them on the **Settings** page
  (or edit `OFF_DAYS` in `data/config.json`, e.g. `["Saturday", "Sunday"]`).
- **Ex employees**: only filled up to the last day they were marked in that month.
- **Not-yet-joined employees** (`added_on` is later) are not touched.

## The settings constants

All three live in `data/config.json` and are edited from the web on the **Settings** page
(nav bar) - no need to touch the file by hand (though you still can):

```json
{ "LATE_TIME": "22:00", "OFFICE_END": "05:00", "OFF_DAYS": ["Saturday"] }
```

- `LATE_TIME` - the office **start**: arriving after this time = status `Late`.
- `OFFICE_END` - the office **end** the next morning. The office runs nights
  (**10:00 PM → 5:00 AM**), so an arrival between `LATE_TIME` and `OFFICE_END`
  (crossing midnight) is Late as well:

  | Arrival | Status | Why |
  |---|---|---|
  | 21:30 | Present | before the shift starts |
  | 22:00 | Present | exactly on time |
  | 22:30 | Late | after the start |
  | 02:30 | Late | inside the shift, but after the start |
  | 05:00 | Late | the cut-off counts as Late |
  | 06:00 | Present | outside the window (early for tonight) |

  (Day-shift style configs, where the start is *before* the end - e.g. 09:00-17:00 - keep
  the simple "after the start = Late" rule.)
- `OFF_DAYS` - weekday names (English, as in `strftime("%A")`) never auto-marked absent.
  The Settings page lists all seven days as checkboxes; untick every day to disable the
  auto-absent fill entirely.

Only marks saved **after** a settings change are judged by the new times; records already
saved keep the status they had.

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
- To view on Google Drive: upload -> right-click -> **Open with > Google Sheets**.

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

`data/transactions.json` + images in `data/uploads/`:

```json
{ "transactions": [
  { "id": "txn_001", "name": "Client A", "date": "2026-10-14",
    "amount": 1500.5, "client": "Acme Corp", "image": "txn_001.png" }
] }
```

All three JSON files are **local-only** (git-ignored) - they never get pushed to GitHub.

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
unknown employee ids are skipped and reported. (Transactions are not part of import.)

## Theme

Dark-green direction used across every page:

| Swatch | Hex | Use |
|--------|-----|-----|
| Lime | `#9FDC56` | accent, buttons, active nav, Present, numbers |
| Pale | `#EAFFD2` | primary text, highlights |
| Coral | `#FF7366` | destructive actions, Absent |
| Blue | `#545FFF` | Leave, secondary chart colour |
| Base | `#161815` | background, text on accent |

Typography: *Neue Montreal* if installed, otherwise the system UI stack. Charts use the same
palette (bars in lime, current month in pale).

## Tests

```bash
python smoke_test.py
```

120 end-to-end checks against a temporary data folder (your real data is not touched).

## Not included (on purpose)

No login (local single-user tool), no network deployment hardening, no payrolls.
Transactions have no CSV/XLSX export yet - see `TODO.md` for the agreed future items.
