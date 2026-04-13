#!/usr/bin/env python3
"""
sync.py — Delta sync triggered on PR merge.

Reads the list of changed .md files (passed as CLI args or via CHANGED_FILES
env var), then upserts or removes the corresponding Google Docs.

Usage:
    python scripts/sync.py docs/service-records/overview.md docs/service-records/endpoints.md

    # Or via env var (used by GitHub Actions):
    CHANGED_FILES="docs/service-records/overview.md" python scripts/sync.py

Environment variables required:
    GOOGLE_SERVICE_ACCOUNT_KEY  — path to service account JSON key file
    GDRIVE_ROOT_FOLDER_ID       — ID of the target folder in Google Drive

Optional:
    DELETED_FILES               — space-separated list of deleted .md files
"""

import json
import os
import sys
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]
REPO_ROOT = Path(__file__).parent.parent
MAP_FILE = REPO_ROOT / "gdoc-map.json"


def get_drive_service():
    key_file = os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def load_map() -> dict:
    if MAP_FILE.exists():
        return json.loads(MAP_FILE.read_text())
    return {}


def save_map(gdoc_map: dict):
    MAP_FILE.write_text(json.dumps(gdoc_map, indent=2) + "\n")


def ensure_folder(service, name: str, parent_id: str) -> str:
    query = (
        f"name='{name}' and mimeType='application/vnd.google-apps.folder' "
        f"and '{parent_id}' in parents and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def upsert_doc(service, file_path: str, gdoc_map: dict, root_folder_id: str):
    """Create or update the Google Doc for a given repo-relative file path."""
    md_file = REPO_ROOT / file_path
    if not md_file.exists():
        print(f"  Skipping (not found): {file_path}")
        return

    doc_id = gdoc_map.get(file_path)

    if doc_id:
        # Update existing doc content
        media = MediaFileUpload(str(md_file), mimetype="text/plain")
        service.files().update(fileId=doc_id, media_body=media).execute()
        print(f"  Updated: {file_path} → {doc_id}")
    else:
        # Create new doc in the correct Drive folder
        parts = Path(file_path).parts  # e.g. ('docs', 'service-records', 'overview.md')
        current_parent = root_folder_id
        for folder_name in parts[:-1]:
            current_parent = ensure_folder(service, folder_name, current_parent)

        metadata = {
            "name": Path(file_path).stem,
            "mimeType": "application/vnd.google-apps.document",
            "parents": [current_parent],
        }
        media = MediaFileUpload(str(md_file), mimetype="text/plain")
        doc = service.files().create(body=metadata, media_body=media, fields="id").execute()
        gdoc_map[file_path] = doc["id"]
        print(f"  Created: {file_path} → {doc['id']}")


def archive_doc(service, file_path: str, gdoc_map: dict):
    """Move a deleted file's Google Doc to trash."""
    doc_id = gdoc_map.pop(file_path, None)
    if not doc_id:
        print(f"  No GDoc found for deleted file: {file_path}")
        return
    service.files().update(fileId=doc_id, body={"trashed": True}).execute()
    print(f"  Archived (trashed): {file_path} → {doc_id}")


def main():
    root_folder_id = os.environ["GDRIVE_ROOT_FOLDER_ID"]
    service = get_drive_service()
    gdoc_map = load_map()

    # Changed files: CLI args take precedence, then env var
    changed_files = sys.argv[1:] if len(sys.argv) > 1 else os.environ.get("CHANGED_FILES", "").split()
    deleted_files = os.environ.get("DELETED_FILES", "").split()

    changed_files = [f for f in changed_files if f.endswith(".md")]
    deleted_files = [f for f in deleted_files if f.endswith(".md")]

    if not changed_files and not deleted_files:
        print("No .md files to sync.")
        return

    for file_path in changed_files:
        upsert_doc(service, file_path, gdoc_map, root_folder_id)

    for file_path in deleted_files:
        archive_doc(service, file_path, gdoc_map)

    save_map(gdoc_map)
    print(f"\nSync complete. Map written to {MAP_FILE}")


if __name__ == "__main__":
    main()
