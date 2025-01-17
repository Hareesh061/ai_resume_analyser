import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from resume_parser import parse_resume


SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
RESUME_FOLDER = 'downloads/'
OUTPUT_FILE = 'Resume_Analysis.xlsx'


# Google Drive Authentication
def authenticate_google_drive():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)


# Download resumes-Google Drive
def download_resumes(drive_service, folder_name='Resumes'):
    if not os.path.exists(RESUME_FOLDER):
        os.makedirs(RESUME_FOLDER)


    results = drive_service.files().list(
        q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id)").execute()
    folder_id = results.get('files', [])[0]['id'] if results.get('files') else None

    if not folder_id:
        print(f"Folder '{folder_name}' not found in Google Drive.")
        return []


    results = drive_service.files().list(
        q=f"'{folder_id}' in parents",
        fields="files(id, name, mimeType)").execute()
    files = results.get('files', [])
    downloaded_files = []

    for file in files:
        file_id = file['id']
        file_name = file['name']
        mime_type = file['mimeType']


        # Handling Google Docs, Sheets
        if mime_type.startswith('application/vnd.google-apps'):
            export_mime_type = 'application/pdf'  

            request = drive_service.files().export_media(fileId=file_id, mimeType=export_mime_type)
        else:
            request = drive_service.files().get_media(fileId=file_id)

        # Save file locally
        file_path = os.path.join(RESUME_FOLDER, f"{os.path.splitext(file_name)[0]}.pdf")
        with open(file_path, 'wb') as f:
            downloader = MediaIoBaseDownload(f, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                print(f"Downloading {file_name} - {int(status.progress() * 100)}%")
        downloaded_files.append(file_path)

    return downloaded_files



# Save res in Excel
def save_to_excel(data):
    df = pd.DataFrame(data)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Results saved to {OUTPUT_FILE}")


def main():
    print("Authenticating with Google Drive...")
    drive_service = authenticate_google_drive()
    
    print("Downloading resumes...")
    resumes = download_resumes(drive_service)
    
    print("Processing resumes...")
    results = []
    for resume in resumes:
        extracted_data = parse_resume(resume)
        results.append(extracted_data)
    
    print("Saving results...")
    save_to_excel(results)

if __name__ == "__main__":
    main()
