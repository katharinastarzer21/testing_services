import os
import shutil
import argparse

def ensure_file(src, dst):
    if not os.path.exists(dst):
        shutil.copy(src, dst)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cookbook_dir", required=True)
    args = parser.parse_args()

    ensure_file("templates/conf.py", os.path.join(args.cookbook_dir, "conf.py"))
    ensure_file("templates/requirements.txt", os.path.join(args.cookbook_dir, "requirements.txt"))