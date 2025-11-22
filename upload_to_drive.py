import os
import sys
import json

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

FOLDER_NAME = "beeMonitorAnalysis"

def get_or_create_folder(service):
    query = f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])

    if files:
        return files[0]["id"]

    folder_metadata = {
        "name": FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder",
    }
    folder = service.files().create(body=folder_metadata, fields="id").execute()
    return folder["id"]


def upload_to_drive(local_path: str, drive_filename: str):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"File not found: {local_path}")

    sa_info = json.loads(os.environ["GDRIVE_SERVICE_ACCOUNT_JSON"])

    creds = service_account.Credentials.from_service_account_info(
        sa_info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )

    service = build("drive", "v3", credentials=creds)

    folder_id = get_or_create_folder(service)

    file_metadata = {
        "name": drive_filename,
        "parents": [folder_id],
    }

    media = MediaFileUpload(local_path, mimetype="text/csv")

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id",
    ).execute()

    print(f"Uploaded to Google Drive. File ID: {file['id']}")


if __name__ == "__main__":
    local_path = sys.argv[1]
    drive_filename = sys.argv[2]

    upload_to_drive(local_path, drive_filename)
