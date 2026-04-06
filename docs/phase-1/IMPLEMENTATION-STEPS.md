# Phase 1 — Implementation steps (Power Platform)

Follow in order. Use **https://make.powerapps.com** with an account that has **Environment Maker** (and **System Administrator** for security roles).

---

## Step 1 — Confirm environment

1. Open **Power Platform admin center** → **Environments**.
2. Select the environment with **Dataverse** (not a Teams-only environment unless that is your deliberate choice).
3. Note the environment URL; all makers use the same environment.

**Exit:** You can open **Tables** in that environment.

---

## Step 2 — Create publisher (if none)

1. **make.powerapps.com** → **Solutions** → **Publishers** (or create solution first — publisher is prompted).
2. Create publisher:
   - **Display name:** RNK Infratech  
   - **Prefix:** `rnk` (3–4 characters)  
   - **Option value prefix:** e.g. `10000` (must not clash with existing in org)

**Exit:** Publisher `rnk` exists.

---

## Step 3 — Create unmanaged solution

1. **Solutions** → **New solution**.
2. **Name:** `RNK Civil Core`  
3. **Publisher:** RNK Infratech (`rnk`).

**Exit:** Empty solution ready; always add new components **into this solution** for ALM.

---

## Step 4 — Create choice columns (global)

1. In solution, **New** → **More** → **Choice** (or create choices while adding columns — either works).
2. Create global choices as listed in [DATAVERSE-SCHEMA.md](./DATAVERSE-SCHEMA.md) section 1:
   - Project status  
   - Pay type  
   - Project access level (if using Project Access table)

**Exit:** Choices available when defining table columns.

---

## Step 5 — Create tables (order matters for lookups)

Create tables **inside the solution** (Add existing / New table from solution).

Suggested order:

1. **OT Rule** — table `rnk_otrule`; add columns from schema doc.
2. **Project** — `rnk_project`.
3. **Site** — `rnk_site`; add lookup **Project** (`rnk_projectid`).
4. **Worker** — `rnk_worker`; add lookups **OT Rule**, **Project** (primary project).
5. **Project Access** (optional) — `rnk_projectaccess`; lookups **User**, **Project**.

For each table:

- Enable **Notes** if you want file attachments later (optional Phase 1).
- **Primary name** column: use as human-readable title (Project name, Site name, etc.).

**Exit:** All tables saved; relationships visible under **Relationships**.

---

## Step 6 — Forms and views

1. Open each table → **Forms** → **Main form**.
2. Add all fields in logical groups (e.g. **General**, **Rates**, **Compliance** on Worker).
3. **Views** → default **Active** views: include key columns for grid editing.

**Worker form tip:** Use **Business Rules** (same table) to show/hide Daily rate vs Monthly gross based on Pay type.

---

## Step 7 — Model-driven app

1. In solution: **New** → **App** → **Model-driven app**.
2. **Name:** `RNK Civil Operations`.
3. **Site map:** Add areas:
   - **Projects** — entity Project (and include related Sites via form subgrid or separate Site list filtered by project).
   - **Directory** — OT Rules, Workers.
   - **Admin** — Project Access (if used).
4. Save and **Publish**.

**Exit:** App URL works; you can create a project, site, OT rule, worker.

---

## Step 8 — Security roles (minimal Phase 1)

1. **Settings** → **Users + permissions** → **Security roles** (or Advanced settings in classic).
2. Clone **Basic User** or create custom roles:
   - **RNK Civil Admin** — Organization-level read/write on custom tables `rnk_*`.
   - **RNK Civil Ops** — User/Business unit level as appropriate; read/write Project, Site, Worker (exclude Finance-only fields when you add field security).
   - **RNK Civil Finance** — read/write Worker (including PAN when field security is on); read Project/Site.

Assign roles to users or Entra groups (group team membership if your tenant supports it).

**Phase 1 simplification:** One **Admin** role with full access to custom tables for all 2–5 users; split roles before go-live if needed.

**Exit:** Non-admin test user can open app and only see allowed data.

---

## Step 9 — Test data

Create in the app:

| Record | Example |
|--------|---------|
| OT Rule | Name: `Double rate`, Multiplier: `2`, Max OT/day: `4` |
| Project | Name: `NH Road Package A`, Status: Active |
| Site | Under project: `Km 12–15 Site Office` |
| Worker | Pay type Daily, Daily rate set, OT rule linked |

**Exit:** Data appears in grids; lookups resolve.

---

## Step 10 — Optional: Power BI

1. **Power BI Desktop** → **Get Data** → **Dataverse**.
2. Connect to environment; select tables `rnk_project`, `rnk_site`, `rnk_worker`, `rnk_otrule`.
3. Build a one-page **Phase 1 inventory**: project count, active workers, sites per project.

**Exit:** Optional dashboard published to workspace.

---

## Troubleshooting

| Issue | Check |
|-------|--------|
| Cannot create table | License includes Dataverse; user has maker role in environment |
| Lookup empty | Parent record saved; user has read privilege on parent table |
| App not visible | Security role includes app module; user has role assigned |

---

## After Phase 1

- Import/retain this repo docs as **versioned spec**.
- For **Phase 2**, add **Attendance** table with lookups to Worker, Site, Project — see main [CIVIL-OPERATIONS-PHASES.md](../CIVIL-OPERATIONS-PHASES.md).

---

*Implementation guide version: 1.0*
