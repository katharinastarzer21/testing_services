import argparse
import yaml
import os
import re

parser = argparse.ArgumentParser()
parser.add_argument("--index", required=True, help="Pfad zur index.md")
parser.add_argument("--title", required=True, help="Projekttitel")
parser.add_argument("--base-path", required=True, help="Basis-Pfad, z.B. production/MYCOOKBOOK/")
parser.add_argument("--output", default="myst.yml", help="Pfad für die zu speichernde myst.yml")
args = parser.parse_args()

# 1. Lese index.md und extrahiere Toctree-Einträge
with open(args.index, "r", encoding="utf-8") as f:
    content = f.read()

# Suche nach {toctree} Block
toctree_pattern = r"```{toctree}.*?```"
toctree_blocks = re.findall(toctree_pattern, content, flags=re.DOTALL)

toc_files = []
for block in toctree_blocks:
    lines = block.splitlines()[1:]  # skip opening ```
    for line in lines:
        line = line.strip()
        if not line or line.startswith(":"):
            continue
        toc_files.append(args.base_path + line)

# 2. Lese ggf. bestehende myst.yml ein
if os.path.exists(args.output):
    with open(args.output, "r", encoding="utf-8") as f:
        myst_config = yaml.safe_load(f)
    if myst_config is None:
        myst_config = {}
else:
    myst_config = {}

# 3. Initialisiere Grundstruktur, falls nötig
if "version" not in myst_config:
    myst_config["version"] = 1
if "project" not in myst_config:
    myst_config["project"] = {}
if "site" not in myst_config:
    myst_config["site"] = {"template": "book-theme"}
if "toc" not in myst_config["project"]:
    myst_config["project"]["toc"] = []

toc = myst_config["project"]["toc"]

# 4. Prüfe, ob Cookbook bereits im TOC ist
cookbook_file = args.base_path + "index.md"
already = False
for entry in toc:
    if entry.get("file") == cookbook_file:
        already = True
        # Optional: aktualisiere die Children, falls sie sich ändern
        entry["children"] = [{"file": f} for f in toc_files]
        break

if not already:
        toc.append({
            "title": args.title,
            "file": cookbook_file,
            "children": [{"file": f} for f in toc_files]
        })

# 5. Schreibe myst.yml zurück
with open(args.output, "w", encoding="utf-8") as f:
    yaml.dump(myst_config, f, sort_keys=False, allow_unicode=True)

print(f"✅ myst.yml wurde aktualisiert: {args.output}")