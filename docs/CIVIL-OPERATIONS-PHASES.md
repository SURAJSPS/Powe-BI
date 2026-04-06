# Civil Operations & Analytics — Phased Implementation

**Stack:** Microsoft 365, Entra ID, Dataverse, Power Apps, Power Automate, Power BI  
**Scope:** Civil / construction daily operations, expenses, attendance, payroll (India), billing, analytics  
**Scale:** 2–5 users (design supports growth)  
**Pay types:** Daily wage, Monthly salary, Overtime  

This document is the single reference for **all phases**, roles, data areas, and governance. Detailed field-level specs can be added in appendices as the build progresses.

---

## 1. Architecture Overview

| Layer | Technology | Purpose |
|-------|------------|---------|
| Identity | Microsoft Entra ID | Sign-in; groups for app roles |
| Data | Microsoft Dataverse | Relational data, security roles, audit |
| Apps | Power Apps (model-driven / canvas) | CRUD, approvals, mobile |
| Automation | Power Automate | Workflows, reminders, period close |
| Analytics | Power BI | Dashboards; align RLS with Dataverse |
| Files (optional) | SharePoint / OneDrive | Attachments; links stored in Dataverse |

**Note:** Power BI is for reporting. Operational truth lives in **Dataverse** (or connected sources), not only in reports.

---

## 2. Roles & Access (RBAC)

Designed for a small team; map real people to one or two roles.

| Role | Typical responsibility | Access summary |
|------|------------------------|----------------|
| **Admin** | Setup, users, masters, exceptions | Full configuration; audit-sensitive overrides |
| **Operations** | Site / PM | Projects, sites, attendance entry & correction requests |
| **Finance** | Accountant | Expenses, payroll runs, billing, statutory fields, exports |
| **Viewer** | Management (optional) | Read-only approved reports and dashboards |

**Implementation:**

- Entra ID security groups (example names): `Civil-Admin`, `Civil-Ops`, `Civil-Finance`, `Civil-Viewer`.
- Dataverse **security roles** aligned to the above; assign users or groups.
- **Field-level security** for sensitive data (e.g. bank account, full salary breakdown) where Ops should not see Finance-only fields.
- **Row-level:** restrict by **project / site** so users only see authorized work.
- **Power BI:** Row-Level Security (RLS) must mirror the same project/role rules (mapping table or same group IDs).

---

## 3. Pay Model (India) — Daily + Monthly + Overtime

### 3.1 Concepts

| Worker pay type | Base calculation | Overtime |
|-----------------|------------------|----------|
| **Daily** | Paid days × daily rate (+ allowances per policy) | OT hours × OT rate (or slab / multiplier from master) |
| **Monthly** | Fixed gross per policy (minus LOP if applicable) | OT on top per policy |

### 3.2 Master data required

- Pay type: Daily / Monthly.
- Base rate and **effective dates** (rates may change).
- **OT rule:** multiplier, hourly vs slab, caps, rounding.
- Optional: allowances and deductions templates.

### 3.3 India compliance (plan fields & reports; confirm with CA)

Statutory items depend on salary, headcount, and **state**: PF, ESI, Professional Tax, LWF, TDS. Store at minimum:

- Worker: state (for PT/LWF), PAN, UAN (PF), ESI IP number where applicable, bank details for payout.
- Payroll run: period, status, approval, lock after payment.

**Hybrid option:** Operations and attendance in Dataverse; statutory payroll run in specialized payroll software — export/import via CSV or integration. Document the chosen approach in Phase 4.

### 3.4 Multi-project labour

If one worker splits time across projects in a month, allocate cost via **timesheet** or **percentage split**. MVP can use **one primary project per worker per month** and refine in a later phase.

---

## Phase 0 — Prerequisites

**Objectives:** Licensing and identity ready before build.

| Item | Action |
|------|--------|
| Licensing | Confirm Power Apps (per user), Dataverse, Power BI Pro/Premium as needed for 2–5 users |
| Groups | Create Entra ID groups for Civil roles |
| Environments | Create or use Power Platform environment (production vs sandbox) |
| Ownership | Name Admin and Finance owners for security and compliance decisions |

**Exit criteria:** Users can sign in; environment exists; licensing verified.

---

## Phase 1 — Foundation (Projects & People)

**Objectives:** Single source of truth for projects, sites, and workers.

### 1.1 Scope

- Projects: create, read, update, archive (prefer archive over hard delete for audit).
- Sites or work orders under projects (civil jobs often need multiple sites per project).
- Worker master with pay type (Daily/Monthly), rates, OT rule link, India-related identifiers as needed.

### 1.2 Core entities (indicative)

| Entity | Purpose |
|--------|---------|
| Project | Header: code, name, client, dates, status, optional budget |
| Site / Work order | Child of project; location, active flag |
| Worker | Identity, contact, pay type, rates, skill, active, bank/statutory fields |
| OT rule | Name, multiplier, hour caps, rounding rules |
| User–project scope (optional) | Which projects each app user may access (for RLS) |

### 1.3 Deliverables

- Power App screens for CRUD on the above.
- Basic validation (required fields, effective dates).
- Optional: simple Power BI list / headcount.

**Implementation package (this repo):** [Phase 1 folder](./phase-1/README.md) — Dataverse schema, step-by-step build, exit checklist.

### 1.4 RBAC

- Admin: full.
- Ops: projects/sites/workers per assigned scope.
- Finance: read workers; write sensitive financial fields per field security policy.
- Viewer: read-only masters if needed.

**Exit criteria:** Projects and workers maintained in app; no duplicate spreadsheets as system of record.

---

## Phase 2 — Attendance

**Objectives:** Authoritative daily attendance and OT for payroll.

### 2.1 Scope

- Daily attendance per worker: date, project/site, shift (if used), status (Present, Absent, Leave, Holiday, Half-day).
- Normal hours and **OT hours** where applicable.
- Approval workflow for corrections to past dates.
- **Attendance period** (e.g. monthly) for India payroll cycles and **lock** after payroll approval.

### 2.2 Core entities (indicative)

| Entity | Purpose |
|--------|---------|
| Attendance | Worker, date, site, status, hours, OT hours, entered by, approval state |
| Attendance period | Start/end, label (e.g. Apr-2026), locked flag |

### 2.3 Logic notes

- Daily workers: paid days + OT drive earnings.
- Monthly workers: define policy for LOP (loss of pay) vs full month; store LOP days if required.

### 2.4 Automation

- Reminders for missing attendance (Power Automate).
- Optional approval when editing locked periods (Admin only with audit).

### 2.5 RBAC

- Ops: enter/edit within scope and open periods.
- Finance: approve locks / corrections per policy.
- Admin: exception handling with full audit.

**Exit criteria:** Monthly attendance extractable for payroll; period lock understood and enforced.

---

## Phase 3 — Expenses & Vendor Spend

**Objectives:** Track project costs and approvals.

### 3.1 Scope

- Expenses: date, project, category (petty cash, fuel, material, hire, etc.), amount.
- GST split optional; bill attachment via SharePoint link.
- Approval workflow (raised → approved).
- Optional: Vendor master (GSTIN, name).

### 3.2 Core entities (indicative)

| Entity | Purpose |
|--------|---------|
| Expense | Header/lines as needed, project, category, amount, tax fields, attachment URL, status |
| Vendor | Optional master for repeat vendors |

### 3.3 RBAC

- Ops: create/submit.
- Finance: approve, full financial view.
- Field-level security on sensitive vendor or amount fields if required.

**Exit criteria:** Expense register by project; approval audit trail.

---

## Phase 4 — Payroll (India)

**Objectives:** Compute and approve pay for Daily + Monthly + OT; statutory summaries per policy.

### 4.1 Scope

- **Payroll run** per period: Draft → Approved → Paid → Locked.
- Pull inputs: attendance, master rates, OT rules, advances/loans (if any).
- Output: payslip lines by component (earnings/deductions).
- Configurable statutory logic or export to external payroll — **decision recorded in Phase 0/4**.

### 4.2 Core entities (indicative)

| Entity | Purpose |
|--------|---------|
| Payroll component | Code, type (earning/deduction), statutory flag |
| Payroll run | Period link, status, approved by, paid date |
| Payslip line | Worker, run, component, amount |
| Advance / loan | Optional; recovery schedule |

### 4.3 Process (high level)

1. Close attendance for period (or import final edits).
2. Compute Daily and Monthly pay per rules + OT.
3. Apply PF, ESI, PT, LWF, TDS per configured rules or export for external tool.
4. Approve run; lock period; generate bank file / summary for payment.

### 4.4 RBAC

- Finance: full payroll operations.
- Ops: no access to payslip amounts (recommended) or summary only.
- Viewer: aggregated reports only.

### 4.5 Decisions (document when starting this phase)

- OT calculation method (hourly multiplier vs slab).
- Monthly: calendar days vs 26/30 for LOP.
- In-app statutory vs hybrid with payroll software.

**Exit criteria:** Approved payroll register for a period; audit trail; period lock.

---

## Phase 5 — Billing & Receivables (India GST)

**Objectives:** Client invoicing and payment tracking.

### 5.1 Scope

- Client master; GSTIN; billing address.
- Invoice: lines, HSN/SAC, CGST/SGST/IGST as applicable, retention, status.
- Receipts against invoices; optional debit/credit notes.

### 5.2 Core entities (indicative)

| Entity | Purpose |
|--------|---------|
| Client | Legal name, GSTIN, address |
| Invoice | Project, numbering, dates, lines, taxes, retention, status |
| Receipt | Invoice link, amount, mode, date |
| Credit/Debit note | Optional |

### 5.3 RBAC

- Finance: full.
- Ops: read-only on status/amounts as per policy.

**Exit criteria:** AR aging and billed vs actual available in reporting.

---

## Phase 6 — Analytics & Governance

**Objectives:** Executive and operational insight; controlled access.

### 6.1 Power BI (indicative dashboards)

- Project P&amp;L: cost vs budget, labour vs material vs other.
- Attendance: reliability, OT trends, by site.
- Payroll: register totals, statutory buckets (as available).
- Cash: billed vs collected, outstanding aging.
- Cross-project KPIs for Viewer role.

### 6.2 Governance

- **Audit** retained on: attendance after lock, payroll, invoices.
- **RLS** in Power BI aligned with Dataverse project scope.
- **Month-end close** checklist (Power Automate or documented SOP).

**Exit criteria:** Role-appropriate dashboards live; refresh schedule defined.

---

## Phase 7 — Hardening & Optional Modules

**Objectives:** Deeper civil workflows and integrations.

| Module | Description |
|--------|-------------|
| Subcontractors | RA bills, retention, TDS on contractor payments |
| Materials / inventory | Issue to site, stock (optional) |
| Equipment | Hire, fuel, maintenance cost tracking |
| Integrations | Export to Tally/Busy; CSV templates |
| Mobile offline | Attendance offline sync — only if connectivity is a problem (extra design) |

Prioritize based on business pain; not all are required for MVP.

---

## Recommended Implementation Order (2–5 users)

1. **Phase 0** — Prerequisites  
2. **Phase 1** — Foundation  
3. **Phase 2** — Attendance  
4. **Phase 4** — Payroll (core to daily/monthly/OT)  
5. **Phase 3** — Expenses  
6. **Phase 5** — Billing  
7. **Phase 6** — Analytics & governance  
8. **Phase 7** — As needed  

*Note:* Phase 4 before Phase 3 is intentional if payroll is the highest risk; if cash visibility is urgent, run Phase 3 in parallel after Phase 2.

---

## Document Control

| Version | Date | Notes |
|---------|------|-------|
| 1.0 | 2026-04-06 | Initial phased documentation |

**Owner:** RNK Infratech IT / project sponsor  
**Review:** Before each phase kickoff (scope, RBAC, India payroll decisions)

---

## Appendix A — Glossary

| Term | Meaning |
|------|---------|
| RLS | Row-Level Security (Power BI / Dataverse row filters) |
| LOP | Loss of pay (unpaid absence) |
| OT | Overtime |
| AR | Accounts receivable |
| BOQ | Bill of quantities |
| GST | Goods and Services Tax (India) |

---

## Appendix B — Pre–Phase 4 Checklist (India Payroll)

Confirm with chartered accountant:

- [ ] PF applicability and employee/employer rates or caps  
- [ ] ESI applicability  
- [ ] Professional Tax and state for each worker  
- [ ] LWF if applicable  
- [ ] TDS on salary slabs  
- [ ] OT policy compliant with applicable labour rules  

---

*End of document*
