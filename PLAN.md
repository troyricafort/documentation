# Docs-as-Code: MD Repo → Google Docs Sync

## Context
The team wants a repo-first documentation workflow where Markdown files are the source of truth. Docs are reviewed via PRs, and on merge a sync script pushes changes to Google Drive (mirroring the repo folder structure). Phase 1 is manual: devs use Claude Code to write MD, open a PR, and merge triggers the sync. Phase 2 (future) will add an automated Claude skill that reads OpenAPI spec artifacts and opens cross-repo PRs automatically.

## What we're building now

A sample repo scaffold at `docs-repo/` demonstrating the full Phase 1 system.

---

## Folder Structure

```
docs-repo/
├── .github/
│   └── workflows/
│       └── sync-to-gdrive.yml     # Triggers on PR merge to main
├── docs/
│   └── service-records/
│       ├── overview.md
│       ├── endpoints.md
│       └── changelog.md
├── scripts/
│   ├── sync.py                    # Delta sync: changed files → Google Docs
│   └── bootstrap.py               # One-time full repo → Drive sync
├── gdoc-map.json                  # Maps file paths → Google Doc IDs
├── requirements.txt
└── README.md
```

---

## Key Files

### `.github/workflows/sync-to-gdrive.yml`
- Triggers on `pull_request` closed + merged to `main`
- Gets changed `.md` files from the PR via GitHub API
- Runs `python scripts/sync.py` with the list of changed files

### `scripts/sync.py`
- Reads `gdoc-map.json` for path → GDoc ID mapping
- For each changed file:
  - If GDoc ID exists → update the existing Google Doc
  - If no GDoc ID → create a new Doc in the correct Drive folder, save ID back to `gdoc-map.json`
  - If file was deleted in PR → mark GDoc as archived
- Commits updated `gdoc-map.json` back to the repo

### `scripts/bootstrap.py`
- One-time script to seed Google Drive from the full repo
- Walks the `docs/` tree, recreates folder structure in Drive
- Creates a Google Doc for each `.md` file
- Writes the full `gdoc-map.json` mapping

### `gdoc-map.json`
```json
{
  "docs/service-records/overview.md": "1abc...GDocId",
  "docs/service-records/endpoints.md": "1def...GDocId"
}
```

---

## GitHub Actions Auth
- Uses a `GOOGLE_SERVICE_ACCOUNT_KEY` repository secret (JSON key for a GCP service account)
- Service account has Drive API write access to the target shared folder

---

## Verification
1. Add or edit any `.md` file → commit to a branch → open PR → merge
2. Workflow fires, `sync.py` runs, only changed files are processed
3. Check Google Drive — the corresponding Doc is created/updated
4. `gdoc-map.json` is updated with any new Doc IDs

---

## Python Dependencies (`requirements.txt`)
- `google-api-python-client` — Drive & Docs API
- `google-auth-httplib2` / `google-auth-oauthlib` — service account auth
- `pypandoc` or `markdown` — MD parsing/conversion
