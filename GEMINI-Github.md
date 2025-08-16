import os
import base64
import requests
from pathlib import Path

# --- Konfiguration ---
TOKEN = "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"
USER = "R3mix9002"
REPO = "KI-monster-philipp"
BRANCH = "main"
WORKING_DIR = "mein_lokaler_ordner" # Ordner, den wir überwachen
API_URL = f"https://api.github.com/repos/{USER}/{REPO}/contents/"

HEADERS = {
"Authorization": f"token {TOKEN}",
"Accept": "application/vnd.github+json"
}

# --- Datei in Base64 kodieren ---
def encode_file(filepath):
with open(filepath, "rb") as f:
return base64.b64encode(f.read()).decode()
 
# --- SHA der Datei im Repo abrufen ---
def get_file_sha(repo_path):
response = requests.get(API_URL + repo_path, headers=HEADERS)
if response.status_code == 200:
return response.json()["sha"]
return None

# --- Datei hochladen oder aktualisieren ---
def upload_file(local_path, repo_path, message="Update Datei"):
content_base64 = encode_file(local_path)
sha = get_file_sha(repo_path)

data = {
"message": message,
"content": content_base64,
"branch": BRANCH
}

action = "Hochgeladen"
if sha:
data["sha"] = sha
action = "Aktualisiert"

r = requests.put(API_URL + repo_path, headers=HEADERS, json=data)
if r.status_code in [200, 201]:
print(f"{action}: {repo_path}")
else:
print(f"Fehler {r.status_code}: {r.json()}")

# --- Datei mergen ---
def merge_file(local_file, repo_file):
sha = get_file_sha(repo_file)
if sha:
# Existierender Inhalt
response = requests.get(API_URL + repo_file, headers=HEADERS)
existing_content = base64.b64decode(response.json()["content"]).decode()
with open(local_file, "r", encoding="utf-8") as f:
local_content = f.read()
merged_content = existing_content + "\n" + local_content
temp_file = local_file + ".merged"
with open(temp_file, "w", encoding="utf-8") as f:
f.write(merged_content)
upload_file(temp_file, repo_file, f"Merge {repo_file}")
os.remove(temp_file)
else:
upload_file(local_file, repo_file, f"Neue Datei {repo_file}")

# --- Automatisches Hochladen aller Dateien im Arbeitsordner ---
def auto_push_merge(local_folder, repo_folder=""):
for root, dirs, files in os.walk(local_folder):
for file in files:
lokal_datei = os.path.join(root, file)
rel_path = os.path.relpath(lokal_datei, local_folder)
repo_datei = os.path.join(repo_folder, rel_path).replace("\\", "/")
merge_file(lokal_datei, repo_datei)

# --- Hauptprogramm ---
if __name__ == "__main__":
print("Starte automatisches Push & Merge...")
auto_push_merge(WORKING_DIR)
print("Fertig! Alle Dateien wurden hochgeladen oder gemerged.")