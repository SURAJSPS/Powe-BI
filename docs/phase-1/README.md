# Phase 1 — Foundation (Projects & People)

**Status:** Ready to implement in Power Platform  
**Prerequisite:** [Phase 0](../CIVIL-OPERATIONS-PHASES.md#phase-0--prerequisites) complete (M365 licensing, Dataverse environment, Entra ID users).

## What Phase 1 delivers

- **Dataverse tables** for projects, sites, OT rules, workers, and optional project access (for later row-level security).
- A **model-driven app** (recommended) or canvas app for **CRUD** on all Phase 1 data.
- **No business logic in Excel** — this repo holds the **spec**; the live system is in your tenant.

## Documents in this folder

| File | Purpose |
|------|---------|
| **[STEP-BY-STEP-DEEP-GUIDE.md](./STEP-BY-STEP-DEEP-GUIDE.md)** | **Full click-by-click walkthrough** (parts A–L): environment, publisher, solution, choices, each table, forms, subgrid, business rules, app, security, test data, Power BI |
| [DATAVERSE-SCHEMA.md](./DATAVERSE-SCHEMA.md) | Table names, fields, types, relationships, choice values |
| [IMPLEMENTATION-STEPS.md](./IMPLEMENTATION-STEPS.md) | Short ordered checklist (same flow, less detail) |
| [../GIT-AND-POWER-PLATFORM.md](../GIT-AND-POWER-PLATFORM.md) | **Git** remote, branches, overview of `pac` |
| [../PAC-SOLUTION-GUIDE.md](../PAC-SOLUTION-GUIDE.md) | **Full guide:** export → `pac` unpack → branch → pack → import + **security** |

## Publisher prefix

Use a single publisher prefix for all custom tables and columns, e.g. **`rnk`** (RNK Infratech). If you choose another prefix, replace `rnk_` everywhere in the schema doc.

## Exit criteria (Phase 1 done when)

- [ ] All tables and relationships exist in Dataverse.
- [ ] Users can create/edit **Project**, **Site**, **OT Rule**, **Worker** from the app.
- [ ] **Archived** projects are used instead of deleting rows (training: archive = status).
- [ ] At least one test project, site, worker, and OT rule exist for Phase 2 testing.

## Next phase

[Phase 2](../CIVIL-OPERATIONS-PHASES.md) — Attendance (builds on Worker + Site + Project).
