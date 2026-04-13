# Documentation Workflow Plan

## Overview

A repo-first documentation system where Markdown files are the source of truth. Docs are version-controlled, reviewed via pull requests, and automatically published to Google Drive on merge — making them accessible to users who don't work in Git.

---

## Core Concept

```
Repo (MD files)  →  PR review  →  Merge  →  Google Drive (Google Docs)
```

- The `docs/` folder in this repo mirrors the folder structure in Google Drive
- Every `.md` file maps 1:1 to a Google Doc
- Users read and reference docs in Google Drive; engineers write and review in Git

---

## Phase 1 — Manual (Current)

Developers use Claude Code to help write and update Markdown files, then follow the standard PR workflow.

### Workflow

1. Developer works on a feature
2. Creates a branch in this repo
3. Uses Claude Code interactively to draft or update the relevant `.md` files
4. Opens a PR — doc changes are reviewed alongside (or independently of) code
5. PR is merged → GitHub Actions triggers `sync.py` → Google Docs updated

### What gets automated

Only the sync to Google Drive is automated. Branch creation, file placement, and PR opening are done manually by the developer.

---

## Phase 2 — Automated Skill (Planned)

A Claude Code skill that reads OpenAPI spec artifacts from the feature repo, generates documentation, and opens a PR in this repo automatically.

### Workflow

1. Developer completes a feature with an OpenAPI spec artifact
2. Runs the Claude Code skill in the feature repo (e.g. `/generate-docs`)
3. Skill reads the spec and generates a summarized, human-readable doc draft
4. Developer reviews and approves the draft
5. Skill opens a cross-repo PR in this docs repo with:
   - The new or updated `.md` files placed in the correct location
   - Updates to any existing files that are relevant to the change
6. PR is reviewed and merged → sync runs as normal

### Cross-repo PR logic

The skill determines file placement by:
- Reading the existing `docs/` tree structure in this repo
- Using Claude to infer the best location based on content similarity and naming conventions
- No static mapping file — Claude reasons about placement from context

### Key design decisions

| Decision | Choice | Reason |
|---|---|---|
| File placement strategy | Claude infers from context | Config files go stale; LLM can reason about evolving structure |
| Spec format | OpenAPI / spec-driven artifacts | Source of truth for what was built |
| PR creation | Via GitHub API (`gh` CLI) | Keeps the skill stateless and portable |
| Doc format | Markdown → Google Docs | Reviewable in Git, readable by non-engineers in Drive |

---

## Google Drive Sync Design

### Folder mirroring

The Drive folder structure matches the repo exactly:

```
docs-repo/docs/service-records/overview.md
                    ↓
Google Drive/docs/service-records/overview  (Google Doc)
```

### gdoc-map.json

A file committed to the repo that maps every `.md` path to its Google Doc ID. This allows the sync script to update existing Docs rather than creating duplicates on every run.

### Bootstrap vs delta sync

| Script | When to run | What it does |
|---|---|---|
| `bootstrap.py` | Once, on first setup | Full walk of `docs/`, creates all Drive folders and Docs |
| `sync.py` | Automatically on every PR merge | Only processes files that changed in the merged PR |

### Deleted files

When a `.md` file is deleted in a PR, `sync.py` moves the corresponding Google Doc to trash and removes it from `gdoc-map.json`.

---

## Repository Secrets Required

| Secret | Description |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_KEY` | JSON key for the GCP service account |
| `GDRIVE_ROOT_FOLDER_ID` | ID of the root Google Drive folder (from its URL) |
