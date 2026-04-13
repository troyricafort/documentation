#!/usr/bin/env python3
"""
bootstrap.py — One-time full sync of the docs/ tree to Google Drive.

Creates the matching folder structure in Drive and converts each .md file
to a Google Doc. Writes a gdoc-map.json file mapping local paths to Doc IDs.

Usage:
    python scripts/bootstrap.py

Environment variables required:
    GOOGLE_SERVICE_ACCOUNT_KEY  — path to service account JSON key file
    GDRIVE_ROOT_FOLDER_ID       — ID of the target folder in Google Drive
"""

import json
import os
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
]
DOCS_DIR = Path(__file__).parent.parent / "docs"
MAP_FILE = Path(__file__).parent.parent / "gdoc-map.json"


def get_drive_service():
    key_file = os.environ["GOOGLE_SERVICE_ACCOUNT_KEY"]
    creds = service_account.Credentials.from_service_account_file(key_file, scopes=SCOPES)
    return build("drive", "v3", credentials=creds)


def ensure_folder(service, name: str, parent_id: str) -> str:
    """Return the Drive folder ID for `name` under `parent_id`, creating it if needed."""
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
    print(f"  Created folder: {name}")
    return folder["id"]


def upload_md_as_gdoc(service, md_path: Path, parent_id: str) -> str:
    """Upload a Markdown file as a Google Doc and return its ID."""
    metadata = {
        "name": md_path.stem,
        "mimeType": "application/vnd.google-apps.document",
        "parents": [parent_id],
    }
    media = MediaFileUpload(str(md_path), mimetype="text/plain")
    doc = service.files().create(body=metadata, media_body=media, fields="id").execute()
    print(f"  Uploaded: {md_path.relative_to(DOCS_DIR.parent)} → Doc ID {doc['id']}")
    return doc["id"]


def main():
    root_folder_id = os.environ["GDRIVE_ROOT_FOLDER_ID"]
    service = get_drive_service()

    gdoc_map = {}
    # Walk docs/ and mirror folder structure into Drive
    for md_file in sorted(DOCS_DIR.rglob("*.md")):
        relative_path = md_file.relative_to(DOCS_DIR.parent)  # e.g. docs/service-records/overview.md
        parts = relative_path.parts  # ('docs', 'service-records', 'overview.md')

        # Ensure every parent folder exists in Drive
        current_parent = root_folder_id
        for folder_name in parts[:-1]:  # skip the filename
            current_parent = ensure_folder(service, folder_name, current_parent)

        doc_id = upload_md_as_gdoc(service, md_file, current_parent)
        gdoc_map[str(relative_path)] = doc_id

    MAP_FILE.write_text(json.dumps(gdoc_map, indent=2) + "\n")
    print(f"\nWrote {len(gdoc_map)} entries to {MAP_FILE}")


if __name__ == "__main__":
    main()
