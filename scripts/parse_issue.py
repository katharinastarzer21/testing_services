import yaml
import sys
import os

preview_mode = "--preview" in sys.argv
print(f"✅ PREVIEW MODE: {preview_mode}")

# Load and print issue body
with open('issue_body.txt') as f:
    body = f.read()

print("Full Issue Body:")
print(body)

# Parse issue fields
fields = {
    "Repository URL": "",
    "Cookbook Title": "",
    "Short Description": "",
    "Thumbnail Image URL": "",
    "Root Path Name": ""
}

lines = body.splitlines()
current_label = None

for line in lines:
    line = line.strip().lstrip("#").strip()
    if line in fields:
        current_label = line
    elif current_label and line:
        fields[current_label] = line
        current_label = None

repo_url = fields["Repository URL"]
title = fields["Cookbook Title"]
description = fields["Short Description"]
thumbnail = fields["Thumbnail Image URL"]
root_path = fields["Root Path Name"]

print(f"🔍 Extracted Fields:")
print(f"→ Repo URL     : {repo_url}")
print(f"→ Title        : {title}")
print(f"→ Description  : {description}")
print(f"→ Thumbnail    : {thumbnail}")
print(f"→ Root Path    : {root_path}")

# Abort if root path is missing
if not root_path:
    print("🛑 ERROR: Root Path could not be extracted – aborting.")
    raise ValueError("Root Path konnte nicht extrahiert werden – Abbruch.")

# Export env vars
with open(os.environ['GITHUB_ENV'], 'a') as env_file:
    env_file.write(f"REPO_URL={repo_url}\n")
    env_file.write(f"ROOT_PATH={root_path}\n")
    env_file.write(f"COOKBOOK_TITLE={title}\n")
    env_file.write(f"COOKBOOK_DESCRIPTION={description}\n")
    env_file.write(f"COOKBOOK_THUMBNAIL={thumbnail}\n")

print("✅ Environment variables exported for GitHub Actions")
