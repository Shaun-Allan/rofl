import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import requests
from urllib.parse import quote
from config import GITLAB_BASE_URL, GITLAB_PERSONAL_ACCESS_TOKEN 


HEADERS = {"PRIVATE-TOKEN": GITLAB_PERSONAL_ACCESS_TOKEN}

TARGETS = [
    # Java CI Templates
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Java/ContinuousIntegrationTemplates", "java8-1.5.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Java/ContinuousIntegrationTemplates", "java17-1.5.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Java/ContinuousIntegrationTemplates", "java21-1.2.0"),
 
    # JavaScript CI Templates
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/JavaScript/ContinuousIntegrationTemplates", "node14-1.4.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/JavaScript/ContinuousIntegrationTemplates", "node20-2.2.0"),
 
    # Python CI Templates
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Python/ContinuousIntegrationTemplates", "python3.10-1.4.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Python/ContinuousIntegrationTemplates", "python3.11-1.4.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Python/ContinuousIntegrationTemplates", "python3.12-1.1.0"),
    ("natwestgroup/EngineeringArtifacts/SoftwareEngineeringLanguages/Python/ContinuousIntegrationTemplates", "main"),
 
    # Scanning Templates
    ("natwestgroup/EngineeringArtifacts/EngineeringComponents/Templates/continuous-integration", "4.0.0"),
]
 
def get_all_files(project_path, ref):
    files = []
    page = 1
    encoded_project = quote(project_path, safe='')
    while True:
        url = f"{GITLAB_BASE_URL}/api/v4/projects/{encoded_project}/repository/tree"
        params = {"recursive": True, "per_page": 100, "page": page, "ref": ref}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f"❌ Failed to fetch file list for {project_path}@{ref}: {response.text}")
            return []
        data = response.json()
        if not data:
            break
        files.extend(data)
        page += 1
    return files
 
def extract_title_from_md(content):
    for line in content.splitlines():
        line = line.strip()
        if line.startswith("#"):
            return line.lstrip("#").strip()
    return "Untitled"
 
def fetch_gitlab_documents(project_path, ref):
    print(f"\n🔍 Scanning {project_path}@{ref} for .md files...\n")
    files = get_all_files(project_path, ref)
    if not files:
        print("⚠️  No files found.\n")
        return
 
    md_files = [f for f in files if f['type'] == 'blob' and f['path'].lower().endswith('.md')]
 
    if not md_files:
        print("⚠️  No .md files found.\n")
        return
 
    for file in md_files:
        encoded_project = quote(project_path, safe='')
        encoded_path = quote(file['path'], safe='')
        url = f"{GITLAB_BASE_URL}/api/v4/projects/{encoded_project}/repository/files/{encoded_path}/raw"
        params = {"ref": ref}
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code == 200:
            content = response.text
            title = extract_title_from_md(content)
            formatted_content = f"{file['path']}\n{title}\n\n{content}"
            return formatted_content
        else:
            return "Failed to fetch", response.status_code