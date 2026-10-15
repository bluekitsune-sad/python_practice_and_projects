# TODO.md - HRMS

## Done (working)

- [x] Flask app, no login, data stored in JSON files (`data/*.json`), run = update = close
- [x] Employees: add / delete, auto ID `emp_001`, optional department + designation
- [x] `Mark ex` soft-delete keeps attendance history; `Delete` removes employee + records (confirmed)
- [x] Manual attendance entry: employee + date (defaults today) + arrival time + hours
- [x] Late-time constant `LATE_TIME = 22:00` in `data/config.json` -> arrival later than that = `Late`
- [x] Re-opening an existing date shows an orange "already has data" warning, prefills it, saving updates
- [x] Automatic status: Present / Late / Absent (checkbox for absent)
- [x] Export by month + year: CSV and XLSX downloads (empty month = message, no empty file)
- [x] Google Sheets friendly: UTF-8 BOM CSV; XLSX with plain YYYY-MM-DD text dates, styled header, colour-coded status, frozen header + filter
- [x] JSON file import: bulk add/update employees and attendance, skips + reports invalid entries
- [x] `smoke_test.py` - 43 end-to-end checks, all passing
- [x] Docs: `README.md` (user), `AGENTS.md` (agents), this file

## Later / if wanted (not built yet - do not build without asking)

- [ ] **Full-detail attendance record**: fields `check_in`, `check_out`, `note` added to each
      record next to `arrival` / `hours` / `status`; extra export columns appear only when
      requested. (Planned per user, storage already easy to extend.)
- [ ] Export polish: per-employee summary block (present/late/absent totals + total hours),
      department column filter, logo/title row
- [ ] Employees page: quick CSV/XLSX download of the employee list
- [ ] Attendance page: month grid/list view showing existing marks at a glance
- [ ] Multi-user/network use -> then, and only then, add simple auth (user said: no login for now)
