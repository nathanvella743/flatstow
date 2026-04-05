#!/usr/bin/env python3

#needed modules
from pathlib import Path
import shutil
import argparse

#argument parser to actually function as a command
parser = argparse.ArgumentParser(description="Link dotfiles to your config directory.")
parser.add_argument("source", nargs='?', help="The folder to sync (defaults to ~/dotfiles or your current working directory)")
parser.add_argument("-d", "--dest", default="~/.config", help="Where to link to (defaults to ~/.config)")
parser.add_argument("--dry-run", action="store_true", help="When this flag is enabled, it doesn't commit anything to your system but tells you what will happen")

args = parser.parse_args()

dotfiles = None
config_folder = Path(args.dest).expanduser().resolve() #destination folder is either ~/.config or provided
backup_folder = config_folder / "Backups"

#set the source folder
if args.source:
    dotfiles = Path(args.source).expanduser().resolve()
elif (Path.home() / "dotfiles").exists():
    dotfiles = (Path.home() / "dotfiles").resolve()
else:
    dotfiles = Path.cwd()

#create the backup folder if needed
if not backup_folder.exists() and args.dry_run == True:
    print(f"[DRY-RUN] Will create a backups folder at {str(backup_folder)}")
elif args.dry_run == False:
    backup_folder.mkdir(exist_ok=True)

print(f"using {str(dotfiles)} as source and {str(config_folder)} as destination")

#loops through source folder
for config in dotfiles.iterdir():
    target: Path = config_folder / config.name
    backup_path: Path = backup_folder / (config.name + ".bak")
             
    if config.name.startswith(".") or config.name == "Backups":
        continue # skips any backup or hidden files or folders
             
    if target.exists() or target.is_symlink():
        # checks for broken links and removes them
        if target.is_symlink() and not target.exists():
            if not args.dry_run:
                target.unlink() 
            else:
                print(f"[DRY-RUN] Will remove broken link at {str(target)}")
        
        # removes any already existing backup files or folders
        if backup_path.exists() or backup_path.is_symlink():
            if not args.dry_run:
                if backup_path.is_symlink():
                    backup_path.unlink()
                elif backup_path.is_dir():
                    shutil.rmtree(backup_path)
                else:
                    backup_path.unlink()
            else:
                print(f"[DRY-RUN] Will remove backup at {str(backup_path)}")
        
        # creates a backup of current file or folder
        if not args.dry_run and target.exists():
            target.rename(backup_path)
        elif target.exists():
            print(f"[DRY-RUN] Will create backup of {str(target)} at {str(backup_path)}")
    
    # creates directories if neede and links folders
    if not args.dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.symlink_to(config)
    else:
        print(f"[DRY-RUN] Will link {target} to {config} and create parent directories if needed")