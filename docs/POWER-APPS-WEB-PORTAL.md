# Power Apps web portal — what to do in the browser

Use **[https://make.powerapps.com](https://make.powerapps.com)** for almost all **Dataverse** and **solution** work.  
**Unpack / pack** (for Git) is **not** in the portal — that needs **`pac`** on your computer ([PAC-SOLUTION-GUIDE.md](./PAC-SOLUTION-GUIDE.md)).

---

## 1. Sign in and pick the environment

1. Open **https://make.powerapps.com**.
2. Sign in with your **work account** (RNK).
3. Top bar → **environment** dropdown → choose the same org every time (e.g. **RNK INFRATECH** / your Dataverse environment).

**Check:** Left navigation shows **Solutions** and **Tables**.

---

## 2. Work with a **solution** (RNK Civil Core)

### Open Solutions

1. Left navigation → **Solutions**.
2. Click your solution name, e.g. **RNK Civil Core**, to open its **Objects** list (tables, apps, etc.).

### Create a new solution (if you have not yet)

1. **Solutions** → **+ New solution**.
2. **Display name:** e.g. `RNK Civil Core`.
3. **Publisher:** choose **RNK Infratech** (or create a publisher with prefix `rnk`).
4. **Save**.

### Add a new table **inside** the solution (recommended)

1. Open **RNK Civil Core**.
2. **Add existing** → **Table** → **Create new table** *or* **New** → **Table** from inside the solution (wording may vary).
3. Follow [STEP-BY-STEP-DEEP-GUIDE.md](./phase-1/STEP-BY-STEP-DEEP-GUIDE.md) for **OT Rule**, **Project**, **Site**, **Worker**.

---

## 3. **Export** a solution (backup or move to another environment)

Do this **after** you **publish** all changes.

### 3.1 Where **Export** actually is (common confusion)

- **Wrong place:** Inside **RNK Civil Core** → **Tables**, the toolbar may show **Export**, but it is often **grayed out** or not the same as “export whole solution as `.zip`” — especially when **Tables (0)** and the solution is still empty.
- **Right place:** Go to the **Solutions list** first, then export the **solution package**.

**Steps:**

1. Left navigation → **Solutions** (click the word **Solutions**, not a sub-item).
2. You should see a **list** of solutions (rows), including **RNK Civil Core**.
3. **Single-click** the row **RNK Civil Core** to select it **without** opening it — or some UIs use a checkbox on the row.
4. Look at the **command bar above the grid** (same level as **New solution** / **Refresh**) → **Export** or **Export solution**.

If you already **opened** the solution (breadcrumb `RNK Civil Core > Tables`), use **← Back** or click **Solutions** in the left nav again to return to the **list**, then select **RNK Civil Core** and use **Export**.

**Note:** Exporting an **empty** solution (0 tables) may still be allowed from the **Solutions list** — useful for backup of the shell — but usually you add tables first, then **Publish all customizations**, then export.

### 3.2 Export wizard (after you click **Export**)

**In the export wizard:**

- Choose **Unmanaged** for development / copying to another dev / later use with `pac` unpack.  
- Choose **Managed** only if your admin says so (often for **production** deployment).

Wait until the package is ready → **Download** the `.zip` file.

**Save** the file somewhere safe (Downloads is fine). This zip is what you can:

- **Import** into another environment (see §4), or  
- **Unpack** with `pac` on your Mac for Git ([PAC-SOLUTION-GUIDE.md](./PAC-SOLUTION-GUIDE.md)).

---

## 4. **Import** a solution (restore or deploy)

1. **Solutions** → **Import** (top) or **Import solution**.
2. **Browse** → select your `.zip` file (exported from another environment or packed by `pac`).
3. **Next** → accept options (overwrite, dependency behaviour) **as your admin instructs**.
4. Wait for **Import successful** → **Publish** customizations if the wizard offers it.

**Note:** First-time import in a new environment may require **missing dependencies** or **connection references** — involve your admin if errors appear.

---

## 5. **Tables** (Dataverse) without opening Solutions first

1. Left navigation → **Tables**.
2. **+ New table** → **Blank table** (for Phase 1 schema).
3. To attach an existing table to your solution: **Solutions** → **RNK Civil Core** → **Add existing** → **Table** → pick the table.

---

## 6. **Model-driven app** (RNK Civil Operations)

1. **Solutions** → open **RNK Civil Core**.
2. **New** → **App** → **Model-driven app** (or **Add existing** if the app already exists).
3. Configure **site map**, add **Project**, **Site**, **Worker**, **OT Rule**, then **Save** and **Publish**.

Or: left nav **Apps** → find **RNK Civil Operations** → **Play** to run the app.

---

## 7. What you **cannot** do only in the web portal

| Task | Where |
|------|--------|
| **Unpack** solution into XML folders for Git | **`pac`** on your PC — [PAC-SOLUTION-GUIDE.md](./PAC-SOLUTION-GUIDE.md) |
| **Pack** folders back into a `.zip` | **`pac`** on your PC |
| Assign **licenses** | **Microsoft 365 admin center** |
| Create **environment** (new Dataverse org) | **Power Platform admin center** → **Environments** |

---

## 8. Related admin portal (not “make”)

| Portal | URL | Use |
|--------|-----|-----|
| **Power Platform admin center** | [https://admin.powerplatform.microsoft.com](https://admin.powerplatform.microsoft.com) | Environments, capacity, settings |
| **Microsoft 365 admin** | [https://admin.microsoft.com](https://admin.microsoft.com) | User licenses |

---

## Quick map: left navigation in make.powerapps.com

| Menu | Typical use |
|------|----------------|
| **Home** | Shortcuts |
| **Solutions** | Export / import **RNK Civil Core**, add tables |
| **Tables** | Create or edit Dataverse tables |
| **Apps** | List apps, **Play** model-driven app |

---

*Phase 1 build steps (tables, forms, app): [phase-1/STEP-BY-STEP-DEEP-GUIDE.md](./phase-1/STEP-BY-STEP-DEEP-GUIDE.md)*
