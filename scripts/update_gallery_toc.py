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
    # Hole alle Zeilen zwischen den toctree-Tags
    lines = block.splitlines()[1:]  # skip opening ```
    for line in lines:
        line = line.strip()
        if not line or line.startswith(":"):
            continue
        # Füge die Datei mit base-path hinzu
        toc_files.append(args.base_path + line)

# 2. Erstelle myst.yml Struktur
myst_config = {
    "version": 1,
    "project": {
        "title": args.title,
        "toc": [
            {
                "file": args.base_path + "index.md",
                "children": [{"file": f} for f in toc_files]
            }
        ]
    },
    "site": {
        "template": "book-theme"
    }
}

# 3. Schreibe myst.yml
with open(args.output, "w", encoding="utf-8") as f:
    yaml.dump(myst_config, f, sort_keys=False)

print(f"✅ myst.yml wurde erstellt: {args.output}")