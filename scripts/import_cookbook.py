import subprocess
import os
import shutil
import argparse

def clone_repo(repo_url, dest_dir):
    subprocess.check_call(['git', 'clone', repo_url, dest_dir])

def copy_repo_to_rootpath(src_repo_dir, dest_cookbook_dir):
    os.makedirs(dest_cookbook_dir, exist_ok=True)
    for item in os.listdir(src_repo_dir):
        if item == ".git":
            continue  # .git-Ordner nicht kopieren
        s = os.path.join(src_repo_dir, item)
        d = os.path.join(dest_cookbook_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo_url', required=True)
    parser.add_argument('--root_path', required=True)
    args = parser.parse_args()

    temp_dir = "_temp_repo"
    clone_repo(args.repo_url, temp_dir)

    dest_dir = os.path.join("cookbooks", args.root_path)
    copy_repo_to_rootpath(temp_dir, dest_dir)