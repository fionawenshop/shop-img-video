import re
import json
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    try:
        creds = Credentials.from_service_account_file('service_account.json', scopes=SCOPES)
        return build('drive', 'v3', credentials=creds)
    except Exception as e:
        print("❌ service_account.json error:", e)
        return None

def extract_folder_id(url):
    match = re.search(r'/folders/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None

def get_folder_name(service, folder_id):
    return service.files().get(fileId=folder_id, fields='name').execute()['name']

def list_all_files(service, parent_id):
    files = []
    page_token = None
    while True:
        resp = service.files().list(
            q=f"'{parent_id}' in parents and trashed=false",
            fields="files(id, name, mimeType), nextPageToken",
            pageToken=page_token,
            pageSize=1000
        ).execute()
        files.extend(resp.get('files', []))
        page_token = resp.get('nextPageToken')
        if not page_token:
            break
    return files

def main():
    url = input("Drive Folder URL: ").strip()
    folder_id = extract_folder_id(url)
    if not folder_id:
        print("Invalid URL")
        return

    service = get_drive_service()
    if not service:
        return

    # 自动获取文件夹真实名称
    folder_name = get_folder_name(service, folder_id)
    
    # 获取当前文件夹下所有文件
    files = list_all_files(service, folder_id)

    # 输出你要的格式：[文件夹名, [文件列表]]
    result = [folder_name, files]
    print(json.dumps(result, ensure_ascii=False))

if __name__ == '__main__':
    main()