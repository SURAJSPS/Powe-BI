# Cursor rules for this repo

**Do not merge these into one giant file.** Cursor applies rule text as context; a single multi‑thousand‑line document dilutes focus, costs more tokens, and mixes “daily coding” with “long roadmap” and “code cookbooks.”

## Cloud / doc-pack filename mapping

If you received the **Streamlit improvements** bundle (`00_START_HERE.md`, `INDEX.md`, `README_IMPROVEMENTS.md`, `QUICK_REFERENCE.md`, etc.), use this table to find the same material **in-repo**:

| Doc pack (Downloads) | This repo (`.cursor/rules/`) | Notes |
|----------------------|------------------------------|--------|
| `IMPLEMENTATION_ROADMAP.md` | `Implementation-roadmap.md` | Same checklist (verified aligned). |
| `ARCHITECTURE_IMPROVEMENTS.md` | `architecture-improvements.md` | Same deep-dive content. |
| `IMPLEMENTATION_EXAMPLES.md` | `Implementation.md` | Same copy-paste examples. |
| `TESTING_GUIDE.md` | `testing-guide.md` | **Merged:** RNK quick reference at the top + full doc-pack strategy (pyramid, `pytest.ini`, fixtures, examples). |
| `README_IMPROVEMENTS.md`, `INDEX.md`, `00_START_HERE.md`, `QUICK_REFERENCE.md` | *No single file* | Orientation / executive summary; overlap with this `README.md` + skim `architecture-improvements.md` + `Implementation-roadmap.md`. |

Cross-references inside `Implementation-roadmap.md` still say `IMPLEMENTATION_EXAMPLES.md` and `TESTING_GUIDE.md` — treat those as **`Implementation.md`** and **`testing-guide.md`** when working only in this repository.

## What to use when

| File | Purpose | Use when |
|------|---------|----------|
| **`python-streamlit-structure.mdc`** | **Canonical** layout: layers, folders, `nav.py`, imports, checklist | Adding features, new pages, refactors |
| **`Implementation-roadmap.md`** | Phased checklist (weeks), milestones | Planning sprints, tracking progress |
| **`architecture-improvements.md`** | Why and what to improve (DI, validation, errors, patterns) | Architecture discussions, ADRs |
| **`Implementation.md`** | Long **code examples** (errors, validation snippets) | Copy-paste while implementing patterns |
| **`testing-guide.md`** | How to test (pytest, layers to hit) | Writing or extending tests |

## Optional consolidation

If you want one entry point:

1. Keep **`python-streamlit-structure.mdc`** as the only **always‑on** rule (or scoped by globs).
2. Add a **short** section at the top of that file: *“See `.cursor/rules/README.md` for roadmap vs examples.”*  
   **Do not** paste all of `Implementation.md` or `architecture-improvements.md` into the `.mdc` file.

---

Renamed: `architecture-improvements·md` → `architecture-improvements.md` (typo in filename).
