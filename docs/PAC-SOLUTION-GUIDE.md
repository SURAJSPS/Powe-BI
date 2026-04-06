# Guide: Export → `pac` unpack → Git → `pac` pack → Import

This is the **hands-on path** for **RNK Civil Core**: move your solution between Power Platform and this repo using **Power Platform CLI (`pac`)**.

---

## Part A — One-time: install `pac` on your Mac

1. Install **.NET** (if you do not have it): [Download .NET](https://dotnet.microsoft.com/download) (SDK or runtime as required by Microsoft’s current `pac` docs).

2. Install the CLI (pick **one** method — follow the latest official page if commands change):

   **Option 1 — .NET tool (common):**

   ```bash
   dotnet tool install --global Microsoft.PowerApps.CLI.Tool
   ```

   **Option 2:** Use **standalone** installer from Microsoft: [Install Power Platform CLI](https://learn.microsoft.com/power-platform/developer/howto/install-cli-net-tool).

3. Confirm:

   ```bash
   pac --version
   ```

   You should see a version number, not “command not found”.

---

## Part B — Export **RNK Civil Core** from Power Apps (browser)

1. Open **[https://make.powerapps.com](https://make.powerapps.com)** and select your environment (e.g. **RNK INFRATECH**).

2. Left menu → **Solutions**.

3. Click **RNK Civil Core** (your Phase 1 solution).

4. Top command bar → **Export** (or **Export solution**).

5. In the wizard:
   - Choose **Unmanaged** for **development** / Git source (typical for unpack/edit cycle).  
   - Use **Managed** when your org’s process says “only managed to production” — your admin decides.

6. Wait for the package to build → **Download** the `.zip` file.

7. Move the file somewhere easy, e.g. **Downloads**:

   `~/Downloads/RNK-Civil-Core.zip`  

   (The exact filename may include a version suffix — that is fine.)

**Note:** You must **publish** all solution changes in Power Apps before export, or the zip will miss the latest tables/forms.

---

## Part C — Sign in to your tenant with `pac` (once per machine / when token expires)

1. List environments (optional):

   ```bash
   pac org list
   ```

   If prompted, sign in in the browser.

2. Or create a profile tied to **one** environment (URL from Power Platform admin center → your environment → **Environment URL**):

   ```bash
   pac auth create --url https://YOURORG.crm8.dynamics.com
   ```

   Replace with **your** org URL (region may be `crm8`, `crm5`, etc.).

3. Check:

   ```bash
   pac auth list
   ```

**Security:** Tokens stay in your **user profile** on the Mac — **not** inside the Git repo. Do not copy `pac` auth files into the project folder.

---

## Part D — Unpack the zip into this repo

1. Go to the project:

   ```bash
   cd "/Users/surajsps/RNK INFRATECH/IT/Powe-BI"
   ```

2. Create a folder for unpacked source:

   ```bash
   mkdir -p solutions/RNK-Civil-Core-unpacked
   ```

3. Unpack (**change the zip path** if your download name differs):

   ```bash
   pac solution unpack --zipfile ~/Downloads/RNK-Civil-Core.zip --folder ./solutions/RNK-Civil-Core-unpacked
   ```

4. If the command succeeds, you will see XML and folders under `solutions/RNK-Civil-Core-unpacked` (e.g. `Entities`, `Other`).

---

## Part E — Simple Git branch workflow

Use **branches** so `main` stays clean and experiments stay separate.

| Branch | When to use |
|--------|-------------|
| **`main`** | Works in Power Platform + you are happy with the unpack. Good for “known good” snapshots. |
| **`develop`** (optional) | Integration before merging to `main`. |
| **`feature/phase-2-attendance`** | New tables/flows for Phase 2 without breaking stable docs on `main`. |

**Example — first time you add the unpacked solution:**

```bash
git checkout main
git pull
git checkout -b feature/rnk-civil-core-unpacked
git add solutions/RNK-Civil-Core-unpacked
git commit -m "Add unpacked RNK Civil Core solution (Phase 1)"
git push -u origin feature/rnk-civil-core-unpacked
```

Then open a **Pull Request** into `main` (if your team uses PRs), or merge locally:

```bash
git checkout main
git merge feature/rnk-civil-core-unpacked
git push
```

**Rule of thumb:** Merge to `main` only after you have **exported** from an environment where Phase 1 was **tested**.

---

## Part F — Pack back to a `.zip` (for import elsewhere)

When you need a file to **Import** into another environment (or restore):

1. Create an output folder (ignored by Git if you use `out/` — see repo `.gitignore`):

   ```bash
   mkdir -p out
   ```

2. Pack:

   ```bash
   pac solution pack --folder ./solutions/RNK-Civil-Core-unpacked --zipfile ./out/RNK-Civil-Core-packed.zip
   ```

3. In the **target** environment: **Solutions** → **Import** → upload `RNK-Civil-Core-packed.zip` → follow prompts (overwrite, layers per your admin).

**Important:** Import order and **managed vs unmanaged** rules depend on your org. Ask your admin before overwriting **production**.

---

## Part G — Security notes (read this)

| Topic | What to do |
|--------|------------|
| **`pac` sign-in** | Stays on your machine; **never** commit auth profiles into Git. |
| **Connection references / secrets** | Real endpoints and secrets belong in **environment variables** or **Azure Key Vault**, not in committed JSON with passwords. |
| **Exported `.zip`** | Usually does **not** contain your login password, but can contain **org-specific IDs**. Treat as **internal**; use a **private** repo. |
| **Public GitHub** | Do **not** push Dataverse solutions to a **public** repository unless your legal/security team approves. |
| **Packed zip in `out/`** | Repo may ignore `out/` so you do not accidentally commit large binaries — adjust `.gitignore` if your team wants to track packed zips (not typical). |

---

## Part H — Quick “every time I change Power Platform” loop

1. **Publish** all changes in [make.powerapps.com](https://make.powerapps.com).  
2. **Solutions** → **RNK Civil Core** → **Export** → download zip.  
3. `pac solution unpack` → **same** `--folder` (overwrite) or new dated folder — your choice.  
4. `git diff` → review → `git commit` → `git push`.

---

## Troubleshooting

| Problem | What to try |
|---------|-------------|
| `pac: command not found` | Reinstall CLI; restart terminal; confirm `dotnet tool` global path is on `PATH`. |
| Unpack fails | Confirm zip is not corrupted; re-download export. |
| Pack fails | Folder must be a valid **unpacked** solution structure (do not delete root `solution.xml`). |
| Import fails in target | Same publisher; environment version; managed/unmanaged rules — ask admin. |

---

## Official references

- [Install Power Platform CLI](https://learn.microsoft.com/power-platform/developer/howto/install-cli-net-tool)  
- [Solution command group](https://learn.microsoft.com/power-platform/developer/cli/reference/solution) (unpack, pack)  

---

*See also: [GIT-AND-POWER-PLATFORM.md](./GIT-AND-POWER-PLATFORM.md)*
