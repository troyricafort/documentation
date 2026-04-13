# docs-repo

Markdown-first documentation repo. Content in `docs/` is the source of truth and syncs to Google Drive automatically when a PR is merged to `main`.

## Workflow

1. Create a branch
2. Add or update `.md` files under `docs/`
3. Open a PR — use Claude Code to help write content if needed
4. Get the PR reviewed and merged
5. GitHub Actions runs `scripts/sync.py` and updates the corresponding Google Docs

## First-time setup

### 1. Google Cloud

- Create a GCP service account with **Google Drive API** enabled
- Download the JSON key
- Share your target Google Drive folder with the service account email (Editor access)

### 2. Repository secrets

| Secret | Description |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_KEY` | Full JSON content of the service account key |
| `GDRIVE_ROOT_FOLDER_ID` | ID of the root folder in Google Drive (from the URL) |

### 3. Bootstrap (first run only)

Seeds Google Drive with the current state of `docs/` and writes `gdoc-map.json`:

```bash
export GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/sa-key.json
export GDRIVE_ROOT_FOLDER_ID=your_folder_id_here
python scripts/bootstrap.py
git add gdoc-map.json && git commit -m "chore: initial gdoc-map" && git push
```

After bootstrap, all future syncs are handled automatically by the GitHub Actions workflow.

## Structure

```
docs/
└── service-records/
    ├── overview.md
    ├── endpoints.md
    └── changelog.md
scripts/
├── bootstrap.py   # one-time full sync
└── sync.py        # delta sync on PR merge
gdoc-map.json      # maps file paths → Google Doc IDs (do not edit manually)
```
# documentation
