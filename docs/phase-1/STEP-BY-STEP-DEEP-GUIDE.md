# Phase 1 — Deep step-by-step guide (Power Platform)

Use this document **from top to bottom** the first time you build Phase 1.  
**Where to work:** [https://make.powerapps.com](https://make.powerapps.com) (and [Power Platform admin center](https://admin.powerplatform.microsoft.com) when noted).

**Names in this guide:** Solution **`RNK Civil Core`**, publisher prefix **`rnk`**. If your admin chose another prefix, replace `rnk` in logical names with yours.

**UI note:** Microsoft changes labels occasionally (“**Solutions**” vs “**Apps**” submenus). If a menu name differs slightly, use the closest match.

---

## Part A — Before you create anything

### A1. Sign in and pick the right environment

1. Go to **https://make.powerapps.com**.
2. Sign in with your **licensed work account** (the one that no longer shows “you’ll need to sign up”).
3. In the **top bar**, open the **environment** dropdown (often shows “Environment name” or “Default”).
4. Select the environment where **Dataverse** is enabled.  
   - If you only see **Teams**-type environments and no database, ask your admin to create a **production** or **sandbox** environment with **Create a database** = **Yes**.

**Check:** Left navigation should include **Tables** (under **Data** or **Dataverse**). If you do not see **Tables**, you are not in a Dataverse environment.

### A2. Confirm you can create solutions

1. Left nav → **Solutions** (under **Solutions**).
2. If **Solutions** opens without error, you have maker access.

**If blocked:** Ask your admin to add you as **Environment Maker** or **System Administrator** for that environment (Power Platform admin center → Environments → your environment → **Settings** → **Users + permissions**).

---

## Part B — Publisher and solution

### B1. Open or create a publisher

1. **Solutions** → **Publishers** (sometimes under **More** or inside **Default Solution** details — if missing: **Solutions** → open any solution → **Publisher** column shows publisher; create new solution in next step and assign publisher).

**Easier path (create publisher while creating solution):**

1. **Solutions** → **+ New solution**.
2. **Display name:** `RNK Civil Core`.
3. **Publisher:** If only **CDS Default Publisher** exists, click **+ New publisher**:
   - **Display name:** `RNK Infratech`
   - **Name:** `RNKInfratech` (no spaces, internal name)
   - **Prefix:** `rnk`
   - **Option value prefix:** e.g. `10000` (use a range your admin approves; avoid clashes with other apps in the same org)
4. Save the publisher, then select it for the solution.
5. **Save** the solution.

**Exit:** You see **RNK Civil Core** in the solution list. **Open** it — all new components should be created **while this solution is open** (or add them to the solution after creation).

### B2. Keep the solution open

For every **new table**, **choice**, or **app**, prefer:

- **Solutions** → **RNK Civil Core** → **Add existing** / **New** — so objects stay in one deployable package.

---

## Part C — Choice columns (global)

You need **three** choice lists for Phase 1 (see [DATAVERSE-SCHEMA.md](./DATAVERSE-SCHEMA.md)).

### C1. Create global choice “Project status”

1. **Solutions** → **RNK Civil Core** → **New** → **More** → **Choice** (if **Choice** is not listed: create the first **Choice** column on the **Project** table in section D3 and select **Sync this choice with new columns** / **Global choice** — both patterns work).

**If using standalone global choice (recommended when available):**

1. **Name (schema):** `rnk_projectstatus` (or wizard default with prefix).
2. **Display name:** `Project status`.
3. Add labels (add each option):
   - Planning  
   - Active  
   - On Hold  
   - Completed  
   - Archived  

**Note:** Numeric values are assigned automatically — that is fine for reporting.

### C2. Global choice “Pay type”

1. Same flow — **Name:** `rnk_paytype`, **Display name:** `Pay type`.
2. Options: **Daily**, **Monthly**.

### C3. Global choice “Project access level” (only if you build **Project Access** table)

1. **Name:** `rnk_projectaccesslevel`.
2. Options: **Read**, **ReadWrite**.

**Exit:** When you add columns to tables, you can pick these global choices.

---

## Part D — Create tables and columns (order matters)

Create tables in this **exact order** so **lookups** resolve:

1. OT Rule  
2. Project  
3. Site  
4. Worker  
5. Project Access (optional)

### D1. Table: OT Rule

1. **Solutions** → **RNK Civil Core** → **New** → **Table** → **Table** (or **New** → **Table**).
2. **Display name:** `OT Rule`  
   **Plural:** `OT Rules`  
3. **Primary column:** Leave default **Name** (schema will be like `rnk_Name`) — set **Display name** to **Rule name** if you want (optional).
4. **Save** the table.

**Add columns** (Table → **Columns** → **+ New column**):

| Display name        | Data type   | Required | Notes                          |
|---------------------|------------|----------|--------------------------------|
| OT multiplier       | Decimal    | Yes      | Min 0, precision per policy    |
| Max OT hours per day| Decimal    | No       |                                |
| Notes               | Multiline text | No   |                                |

**Save** each column.

**Relationship:** None required.

---

### D2. Table: Project

1. **New** → **Table** → **Display name:** `Project`, **Plural:** `Projects`.
2. Primary **Name** column → use as **Project name**.

**Add columns:**

| Display name   | Data type        | Required | Notes                                      |
|----------------|------------------|----------|--------------------------------------------|
| Project code   | Text             | No       | Single line; max length e.g. 20            |
| Client name    | Text             | No       |                                            |
| Start date     | Date only        | No       | Date only, not date/time                   |
| End date       | Date only        | No       |                                            |
| Status         | Choice           | Yes      | Use global **`rnk_projectstatus`**         |
| Budget         | Currency         | No       | Base currency of environment               |
| Description    | Multiline text   | No       |                                            |

**Default for Status:** In column properties, set **Default value** to **Active** or **Planning** if the designer allows.

**Save** the table.

---

### D3. Table: Site (lookup to Project)

1. **New** → **Table** → **Site** / **Sites**.

**Add columns:**

| Display name | Data type | Required | How to create |
|--------------|-----------|----------|----------------|
| Project      | Lookup    | Yes      | **Related table:** **Project** — this creates **Many-to-one** Site → Project |

Then add:

| Display name | Data type      | Required |
|--------------|----------------|----------|
| Location     | Text           | No       |
| Active       | Yes/No         | Yes      | Default **Yes** |

**Save.**

**Verify relationship:** Open table **Site** → **Relationships** — you should see **Project** (Many Site records to one Project).

---

### D4. Table: Worker (lookups + pay fields)

1. **New** → **Table** → **Worker** / **Workers**.

**Add columns in a sensible order:**

| Display name        | Data type      | Required | Notes |
|---------------------|----------------|----------|--------|
| Phone               | Phone          | No       | |
| Pay type            | Choice         | Yes      | Global **`rnk_paytype`** |
| Daily rate          | Currency       | No       | Enforced by business rule below |
| Monthly gross       | Currency       | No       | |
| OT rule             | Lookup         | No       | **Related table:** **OT Rule** |
| Rate effective from | Date only      | No       | |
| Skill / role        | Text           | No       | |
| India state         | Text           | No       | Or convert to Choice later |
| PAN                 | Text           | No       | |
| Active              | Yes/No         | Yes      | Default **Yes** |
| Primary project     | Lookup         | No       | **Related table:** **Project** |

**Save** the table.

---

### D5. Optional: Table Project Access

Skip for 2–5 users if everyone is admin; add if you need **per-user project scope** early.

1. **New** → **Table** → **Project Access**.

**Columns:**

| Display name   | Data type | Required | Notes |
|----------------|-----------|----------|--------|
| User           | Lookup    | Yes      | Related table: **User** (system user) |
| Project        | Lookup    | Yes      | Related table: **Project** |
| Access level   | Choice    | Yes      | Global **`rnk_projectaccesslevel`** |

**Primary name:** Either keep **Name** and fill manually, or add a **Formula** column later — for Phase 1, manual **Name** like `UserName - ProjectCode` is OK.

---

## Part E — Forms and views

### E1. Main forms — add sections

For each table (**OT Rule**, **Project**, **Site**, **Worker**):

1. **Tables** → select table → **Forms** → open **Main** form (Information).
2. **Save as** only if you want a backup; usually edit the default main form.
3. Drag a **Section** (e.g. **General**, **Rates**, **Compliance** on Worker).
4. Drag fields from **Table columns** into the section.
5. **Save** → **Publish**.

### E2. Project form — Sites subgrid

1. Open **Project** main form.
2. Add a **Subgrid** control.
3. **Related entity:** **Sites** (records related to this Project via lookup).
4. **Default view:** Active Sites.
5. **Save** → **Publish**.

### E3. Views

For each table:

1. **Tables** → table → **Views** → open **Active [Table]s** (or create a new view).
2. **Add columns** you need in the list (Project code, Status, Client, etc.).
3. **Save** → **Publish**.

---

## Part F — Business rules (Worker pay fields)

Goal: If **Pay type** = Daily, **Daily rate** is required; if Monthly, **Monthly gross** is required.

1. **Tables** → **Worker** → **Business rules**.
2. **New business rule**.
3. **Condition:** **Pay type** **Contains value** **Daily** (or equals Daily — depends on choice editor).
4. **Action:** **Set field level error** on **Daily rate** if empty — *or* **Set visibility** / **Set requirement** for **Daily rate** = **Required** when condition true.

**Repeat** for Monthly: if **Pay type** = **Monthly**, require **Monthly gross**.

Alternatively use **Power Fx** on a **Canvas** app — for **model-driven**, business rules are the usual approach.

**Activate** the business rule → **Save** → **Publish**.

---

## Part G — Model-driven app

### G1. Create the app

1. **Solutions** → **RNK Civil Core** → **New** → **App** → **Model-driven app**.
2. **Name:** `RNK Civil Operations`.
3. **Use existing solution** — stay in **RNK Civil Core**.

Modern designer:

1. Open the app in the **app designer**.
2. **Site map** (left) → **New area**, e.g. **Work** or **Civil**.
3. **Group** → **Subarea** → **Entity** → select **Project**.
4. Add another subarea for **Site**, **Worker**, **OT Rule**.
5. If you use **Project Access**, add under an **Admin** group.

**Forms:** Ensure **Main form** is selected for each entity.

### G2. Publish

1. **Save**.
2. **Publish** the app (top command bar).

### G3. Play / URL

1. **Apps** → find **RNK Civil Operations** → **Play** (or open from solution).
2. Bookmark the URL for your team.

---

## Part H — Security roles

### H1. Why this matters

Without the right **security role**, users see **empty lists** or **cannot save**.

### H2. Create a simple Phase 1 role (all makers full access)

1. **make.powerapps.com** → **Settings** (gear) → **Advanced settings** (if available) **OR** go to [Power Platform admin center](https://admin.powerplatform.microsoft.com) → **Environments** → your environment → **Settings** → **Users + permissions** → **Security roles**.

**Classic path (still used):**

1. **Advanced settings** → **Settings** → **Security** → **Security roles**.
2. **New** — or **Copy** an existing role (e.g. **Basic User**).

**Name:** `RNK Civil Admin`.

**Core tables tab:** Find your custom tables (**OT Rule**, **Project**, **Site**, **Worker**, **Project Access** if any).

For each **Entity**:

- Set **Create**, **Read**, **Write**, **Delete**, **Append**, **Append To** as needed.  
- For Phase 1 internal testing: **Organization** scope for **Read/Write** on these entities (simplest for 2–5 trusted users).

**Save** the role.

### H3. Assign role to users

1. **Advanced settings** → **Settings** → **Security** → **Users**.
2. Open a user → **Manage roles** → add **RNK Civil Admin** (and **Basic User** / **Microsoft Dataverse User** if required by your tenant).

**Or:** Power Platform admin center → **Users** → select user → **Manage roles**.

### H4. Give access to the model-driven app

Some tenants require the **app module** to be visible:

1. In **Security role**, find tab **Customizations** / **Business Management** / **App** modules — or add the app to **Model-driven apps** access depending on version.
2. Often assigning **Environment Maker** + table privileges is enough; if the app does not appear, add user to a **Team** that owns the app or publish app to **All roles** in app properties.

**Troubleshooting:** If user sees no entities, **privileges** on custom tables are almost always the cause.

---

## Part I — End-to-end test (test data)

### I1. Create records in this order

1. **OT Rule**  
   - Rule name: `Double rate`  
   - OT multiplier: `2`  
   - Max OT hours per day: `4` (optional)

2. **Project**  
   - Project name: `NH Road Package A`  
   - Status: **Active**  
   - Client name: `NHAI` (example)

3. **Site**  
   - Site name: `Km 12–15 Site Office`  
   - **Project** = above project  
   - Active: **Yes**

4. **Worker**  
   - Full name: `Test Worker One`  
   - Pay type: **Daily**  
   - Daily rate: e.g. `800` INR  
   - OT rule: `Double rate`  
   - Active: **Yes**  
   - Primary project: same project (optional)

### I2. Validate

- Open **Project** — subgrid shows **Site**.  
- Open **Worker** — lookups show **OT Rule** and **Project**.  
- Try saving Worker with wrong pay type vs rate — business rule should block or warn.

---

## Part J — Optional: Power BI

1. Install **Power BI Desktop**.
2. **Get data** → **Power Platform** → **Dataverse**.
3. Sign in; pick **environment** and **Dataverse** URL if prompted.
4. Select tables: `rnk_project`, `rnk_site`, `rnk_worker`, `rnk_otrule` (names may show with display names).
5. **Load** → build a simple table visual: count of projects, count of workers.
6. **Publish** to a workspace (needs **Power BI Pro** or Premium per your org).

---

## Part K — Troubleshooting checklist

| Symptom | Likely fix |
|---------|------------|
| “You need a security role” | Assign **RNK Civil Admin** + **Basic User** / Dataverse user role |
| Empty grid in app | User lacks **Read** on entity; scope too narrow — try **Organization** read for test |
| Cannot create table | Wrong environment; not a Dataverse environment |
| Lookup empty | No rows in parent table; user cannot read parent table |
| Business rule not firing | Rule not **Activated**; form not refreshed |
| App not in list | App not **Published**; user not in environment |

---

## Part L — What to do after Phase 1

1. Freeze the **RNK Civil Core** solution as “Phase 1 baseline” (export unmanaged/managed per your ALM policy).
2. Open [../CIVIL-OPERATIONS-PHASES.md](../CIVIL-OPERATIONS-PHASES.md) and plan **Phase 2 — Attendance** (new table + links to Worker, Site, Project).

---

*Deep guide version: 1.0 — aligns with DATAVERSE-SCHEMA.md*
