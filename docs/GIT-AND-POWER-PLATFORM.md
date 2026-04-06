# Git + Power Platform (RNK Civil)

This repo holds **documentation and specs**. Your **Dataverse solution** (tables, app) still lives in Power Platform; Git stores **versioned docs** and optionally **unpacked solution source** after you use the **Power Platform CLI (`pac`)**.

---

## 1. Initialize Git (once on your machine)

From the project folder:

```bash
cd "/Users/surajsps/RNK INFRATECH/IT/Powe-BI"
git status
```

If Git is already initialized, you will see branch and file status. If not:

```bash
git init
git add docs/
git commit -m "Add Civil Operations docs and Phase 1 specifications"
```

---

## 2. Connect to a remote (GitHub, Azure DevOps, etc.)

Create an **empty** repository on your provider, then:

```bash
git remote add origin <YOUR_REPO_URL>
git branch -M main
git push -u origin main
```

Use **HTTPS** or **SSH** depending on your org. RNK IT may require Azure DevOps or a private GitHub org — follow internal policy.

---

## 3. What to commit in this repo

| Commit | Reason |
|--------|--------|
| `docs/**` | Specs, phase guides, schema — **always** |
| Unpacked solution under e.g. `solutions/RNK-Civil-Core/` | Optional — after `pac solution unpack` (see below) |
| `*.zip` exports | Optional — often **excluded** (large); use **Artifacts** or **Git LFS** if needed |

---

## 4. Track the Power Platform **solution** in Git (optional ALM)

**Flow:**

1. Build **RNK Civil Core** in [make.powerapps.com](https://make.powerapps.com) (Phase 1).
2. **Solutions** → **RNK Civil Core** → **Export** → download `.zip`.
3. Install **Power Platform CLI**: [Install Power Platform CLI](https://learn.microsoft.com/power-platform/developer/cli/introduction).
4. Unpack next to this repo (example paths):

```bash
mkdir -p solutions
pac solution unpack --zip-file ~/Downloads/RNK-Civil-Core.zip --folder ./solutions/RNK-Civil-Core-unpacked
```

5. Commit the **unpacked** folder (or pack from CI — team choice):

```bash
git add solutions/RNK-Civil-Core-unpacked
git commit -m "Unpack RNK Civil Core solution for source control"
git push
```

**Pack** (to produce a zip from source for import elsewhere):

```bash
pac solution pack --folder ./solutions/RNK-Civil-Core-unpacked --zipfile ./out/RNK-Civil-Core-packed.zip
```

Then **Solutions** → **Import** in the target environment.

**Auth for `pac`:**

```bash
pac auth create --environment <YOUR_ENVIRONMENT_URL_OR_ID>
```

Use the environment URL from Power Platform admin center.

---

## 5. Branching (simple)

| Branch | Use |
|--------|-----|
| `main` | Stable docs + tested solution unpack |
| `develop` or `feature/phase-2-attendance` | Work in progress |

Merge to `main` after Phase 1 (or each phase) is verified in Dataverse.

---

## 6. Security

- Do **not** commit **client secrets**, **refresh tokens**, or **connection strings** with passwords.
- `pac` auth profiles live under your user profile — not usually in the repo; keep `.gitignore` as-is unless your team adds a secrets pattern.

---

## 7. Daily workflow (short)

1. Edit docs in Cursor → `git add` → `git commit` → `git push`.
2. After changes in Power Platform → **Export** solution → unpack → commit → push.
3. Teammates **pull** → **pack** (if using unpacked source) → **Import** to their sandbox (or use a shared dev environment).

---

*See also: [phase-1/README.md](./phase-1/README.md)*
