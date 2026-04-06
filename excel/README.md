# RNK Civil — Excel workbook (all phases)

## File

| File | Description |
|------|-------------|
| **`RNK_Civil_Operations_AllPhases.xlsx`** | Master workbook: master data, attendance, expenses, payroll helpers, billing, dashboard. |
| **`generate_rnk_civil_workbook.py`** | Regenerates the `.xlsx` (overwrites). Use after editing the script. |

## Regenerate

```bash
cd "/Users/surajsps/RNK INFRATECH/IT/Powe-BI"
. .venv/bin/activate
python excel/generate_rnk_civil_workbook.py
```

Requires **Python 3** + **openpyxl** (included in project `.venv`).

## Sheets (by phase)

| Phase | Sheets |
|-------|--------|
| **1** | `Setup_OTRules`, `Projects`, `Sites`, `Workers` |
| **2** | `Attendance` |
| **3** | `Expenses` |
| **4** | `Period_Control`, `AttendanceSummary`, `PayrollRuns`, `PayrollLines` |
| **5** | `Invoices`, `InvoiceLines` |
| **6** | `Dashboard` |
| — | `Instructions` |

## Notes

- **Period_Control** (`B2`–`B3`) drives date filters in **AttendanceSummary** and **Dashboard**.
- **AttendanceSummary** formulas are **estimates**; statutory PF/ESI/PT/TDS belong in **PayrollLines** with your CA’s rules.
- Keep the file on **SharePoint/OneDrive** with **version history**; avoid emailing copies as the system of record.
