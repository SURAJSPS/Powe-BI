# Phase 1 — Dataverse schema specification

Use this document when creating tables in **make.powerapps.com** → **Tables**.  
**Naming:** Replace `rnk` with your publisher prefix if different.

---

## 1. Global choice lists (create once, reuse)

Create these as **Choice** columns (global choice set) or **local choice** per table — global is easier for reporting.

### Choice: Project status (`rnk_projectstatus`)

| Value | Label |
|-------|--------|
| 100000001 | Planning |
| 100000002 | Active |
| 100000003 | On Hold |
| 100000004 | Completed |
| 100000005 | Archived |

### Choice: Pay type (`rnk_paytype`)

| Value | Label |
|-------|--------|
| 100000001 | Daily |
| 100000002 | Monthly |

### Choice: Project access level (`rnk_projectaccesslevel`) — optional table

| Value | Label |
|-------|--------|
| 100000001 | Read |
| 100000002 | ReadWrite |

*Note:* Dataverse auto-assigns numeric values; align labels as above when creating choices.*

---

## 2. Table: OT Rule (`rnk_otrule`)

**Display name:** OT Rule  
**Plural:** OT Rules  
**Primary column:** Name (standard) — use as **Rule name** (e.g. “Standard 2x OT”).

| Logical name | Display name | Type | Required | Description |
|--------------|--------------|------|----------|-------------|
| `rnk_name` | (Primary name) | Text | Yes | Rule name |
| `rnk_multiplier` | OT multiplier | Decimal | Yes | e.g. 2.0 for double rate |
| `rnk_maxothoursperday` | Max OT hours per day | Decimal | No | Cap if policy limits |
| `rnk_notes` | Notes | Multiline text | No | Rounding, slab rules in text until Phase 4 |

**Relationships:** None required for Phase 1 (referenced by Worker).

---

## 3. Table: Project (`rnk_project`)

**Display name:** Project  
**Plural:** Projects  
**Primary column:** Name — project title.

| Logical name | Display name | Type | Required | Description |
|--------------|--------------|------|----------|-------------|
| `rnk_name` | Project name | Text (primary) | Yes | |
| `rnk_projectcode` | Project code | Text | No | Short code; unique enforced in app or alternate key |
| `rnk_clientname` | Client name | Text | No | |
| `rnk_startdate` | Start date | Date only | No | |
| `rnk_enddate` | End date | Date only | No | |
| `rnk_status` | Status | Choice (`rnk_projectstatus`) | Yes | Default: Planning or Active |
| `rnk_budgetamount` | Budget | Currency | No | Optional baseline |
| `rnk_description` | Description | Multiline text | No | |

**Validation ideas (Phase 1):** Business rule or app: `End date >= Start date` when both set.

**Alternate key (optional):** `rnk_projectcode` if you need uniqueness.

---

## 4. Table: Site (`rnk_site`)

**Display name:** Site  
**Plural:** Sites  

| Logical name | Display name | Type | Required | Description |
|--------------|--------------|------|----------|-------------|
| `rnk_name` | Site name | Text (primary) | Yes | |
| `rnk_projectid` | Project | Lookup → Project | Yes | Parent project |
| `rnk_location` | Location | Text | No | Address or landmark |
| `rnk_isactive` | Active | Yes/No | Yes | Default: Yes |

**Relationship:** Many Sites → one Project (`rnk_projectid`).

**Subgrid:** Add Sites subgrid on Project main form.

---

## 5. Table: Worker (`rnk_worker`)

**Display name:** Worker  
**Plural:** Workers  

| Logical name | Display name | Type | Required | Description |
|--------------|--------------|------|----------|-------------|
| `rnk_name` | Full name | Text (primary) | Yes | |
| `rnk_phonenumber` | Phone | Phone | No | |
| `rnk_paytype` | Pay type | Choice (`rnk_paytype`) | Yes | Daily or Monthly |
| `rnk_dailyrate` | Daily rate | Currency | No | Required when Pay type = Daily (enforce in app/rule) |
| `rnk_monthlygross` | Monthly gross | Currency | No | Required when Pay type = Monthly |
| `rnk_otruleid` | OT rule | Lookup → OT Rule | No | Default OT calculation |
| `rnk_rateeffectivedate` | Rate effective from | Date only | No | For rate changes |
| `rnk_skill` | Skill / role | Text | No | Mason, supervisor, etc. |
| `rnk_indiastate` | India state | Text | No | For PT/LWF (Phase 4); optional choice list later |
| `rnk_pan` | PAN | Text | No | Mask/sensitivity in Phase 4 |
| `rnk_active` | Active | Yes/No | Yes | Default: Yes |
| `rnk_primaryprojectid` | Primary project | Lookup → Project | No | MVP cost allocation; optional |

**Business rules (recommended):**

- If `rnk_paytype` = Daily → require `rnk_dailyrate` (or show error on save).
- If `rnk_paytype` = Monthly → require `rnk_monthlygross`.

---

## 6. Table: Project access (optional, for later RLS) (`rnk_projectaccess`)

**Display name:** Project Access  
**Plural:** Project Accesses  

Use this when you need **which user can see which project** beyond owner team. For 2–5 users you can skip initially and add in Phase 6.

| Logical name | Display name | Type | Required | Description |
|--------------|--------------|------|----------|-------------|
| `rnk_name` | Name | Text (primary) | Yes | Auto: User + Project or manual label |
| `rnk_systemuserid` | User | Lookup → User | Yes | Dataverse system user |
| `rnk_projectid` | Project | Lookup → Project | Yes | |
| `rnk_accesslevel` | Access level | Choice (`rnk_projectaccesslevel`) | Yes | Read vs ReadWrite |

**Relationship:** Many Project Access → one User; many → one Project.

**Alternate:** Use **Teams** per project instead of this table — document whichever you choose.

---

## 7. Relationship summary

```
Project (1) ──< (N) Site
OT Rule (1) ──< (N) Worker   [optional lookup]
Project (1) ──< (N) Worker  [optional rnk_primaryprojectid]
User (1) ──< (N) Project Access ──> (N) Project
```

---

## 8. Field security (Phase 1 light touch)

For Phase 1, optional:

- **PAN** on Worker: enable **Field security**; grant **Finance** and **Admin** profiles full access; **Operations** none or read-only if needed.

Full matrix comes with Phase 4 payroll fields.

---

## 9. Solution contents checklist

Add to a single solution (e.g. **RNK Civil Core**):

- [ ] Tables: OT Rule, Project, Site, Worker, Project Access (if used)
- [ ] Choices linked as above
- [ ] Model-driven app **RNK Civil Operations**
- [ ] Security roles: at minimum extend **Basic User**; add **RNK Civil Admin**, **RNK Civil Ops**, **RNK Civil Finance** in Phase 1 or start of Phase 2

---

*Schema version: 1.0 — Phase 1*
