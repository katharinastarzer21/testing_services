import yaml
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--path", required=True, help="Pfad zur index.md z. B. production/my-cookbook/index.md")
parser.add_argument("--title", required=True, help="Anzeigetitel im TOC")
parser.add_argument("--toc_file", default="myst.yml", help="Pfad zur myst.yml Datei")
parser.add_argument("--section", default="Cookbook Gallery", help="TOC-Abschnittsname")
args = parser.parse_args()

if not os.path.exists(args.toc_file):
    print(f"🛑 {args.toc_file} not found – aborting.")
    exit(1)

with open(args.toc_file, "r") as f:
    config = yaml.safe_load(f)

config.setdefault("project", {})
config["project"].setdefault("toc", [])
toc = config["project"]["toc"]

file_path = args.path

section_found = False
for entry in toc:
    if entry.get("title") == args.section:
        section_found = True
        entry.setdefault("children", [])

        already_exists = any(child.get("file") == file_path for child in entry["children"])
        if not already_exists:
            entry["children"].append({
                "title": args.title,
                "file": file_path
            })
            print(f"✅ Added {file_path} under '{args.section}'")
        else:
            print(f"ℹ️ {file_path} already exists under '{args.section}'")
        break

if not section_found:
    print(f"🆕 Creating section '{args.section}' and adding first entry")
    toc.append({
        "title": args.section,
        "children": [
            {
                "title": args.title,
                "file": file_path
            }
        ]
    })

# myst.yml speichern
with open(args.toc_file, "w") as f:
    yaml.dump(config, f, sort_keys=False)
