import yaml
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("--path", required=True, help="Path to inserted index.md (e.g. production/my-cookbook/index.md)")
parser.add_argument("--title", required=True, help="Displayed title")
parser.add_argument("--toc_file", default="myst.yml", help="Path to myst.yml")
parser.add_argument("--section", default="Cookbook Gallery", help="Title of section to insert under")
args = parser.parse_args()

if not os.path.exists(args.toc_file):
    print(f"🛑 {args.toc_file} not found – aborting.")
    exit(1)

with open(args.toc_file, "r") as f:
    config = yaml.safe_load(f)

if "project" not in config:
    config["project"] = {}
if "toc" not in config["project"]:
    config["project"]["toc"] = []

toc = config["project"]["toc"]

# Suche nach Abschnitt "Cookbook Gallery"
section_found = False
for entry in config["toc"]:
    if entry.get("title") == args.section:
        section_found = True
        if "children" not in entry:
            entry["children"] = []

        already_exists = any(child.get("file") == args.path for child in entry["children"])
        if not already_exists:
            entry["children"].append({
                "title": args.title,
                "file": args.path
            })
            print(f"✅ Added {args.path} under '{args.section}'")
        else:
            print(f"ℹ️ {args.path} already exists under '{args.section}'")
        break

# Wenn "Cookbook Gallery" noch nicht existiert
if not section_found:
    print(f"🆕 Creating section '{args.section}' and adding first entry")
    config["toc"].append({
        "title": args.section,
        "children": [
            {
                "title": args.title,
                "file": args.path
            }
        ]
    })

# Speichern
with open(args.toc_file, "w") as f:
    yaml.dump(config, f, sort_keys=False)
