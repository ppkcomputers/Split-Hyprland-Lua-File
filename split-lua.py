#!/usr/bin/env python3
import os
import re
import shutil
import sys
import urllib.request

# Determine the config directory universally (honors XDG_CONFIG_HOME, defaults to ~/.config)
XDG_CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
HYPR_DIR = os.path.join(XDG_CONFIG_DIR, "hypr")
MAIN_CONFIG = os.path.join(HYPR_DIR, "hyprland.lua")
CONFIGS_SUBDIR = os.path.join(HYPR_DIR, "configs")

# Official default template URL directly from the Hyprland upstream repository
DEFAULT_CONFIG_URL = "https://raw.githubusercontent.com/hyprwm/Hyprland/main/example/hyprland.lua"

def clean_filename(title):
    # Strip any leading/trailing dashes and spaces from the title
    cleaned = title.strip("-").strip()
    # Replace spaces or symbols with underscores
    cleaned = re.sub(r'[\(\)\-\/]', '_', cleaned)
    cleaned = re.sub(r'\s+', '_', cleaned)
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned.lower().strip("_")

def download_default_config():
    print(f"\nCreating directory: {HYPR_DIR}")
    os.makedirs(HYPR_DIR, exist_ok=True)

    print("Downloading official default hyprland.lua template...")
    try:
        # Download the file natively using Python's standard library
        urllib.request.urlretrieve(DEFAULT_CONFIG_URL, MAIN_CONFIG)
        print(f"\033[92m[✓] Successfully downloaded default template to {MAIN_CONFIG}!\033[0m")
        print("You can now run this script again to split your newly downloaded config.")
    except Exception as e:
        print(f"\033[91m[!] Error downloading file: {e}\033[0m")

def split_config():
    # 1. CHECK IF FILE EXISTS
    if not os.path.exists(MAIN_CONFIG):
        print(f"\033[91m[!] Error: Could not find main config at {MAIN_CONFIG}\033[0m")
        print("\nIf you want to download a default 'hyprland.lua' template manually, run this command:")
        print(f"\033[96mcurl -Lo ~/.config/hypr/hyprland.lua {DEFAULT_CONFIG_URL}\033[0m\n")

        # Interactive prompt to download automatically
        choice = input("Would you like this script to download the default template for you now? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            download_default_config()
        else:
            print("Exiting.")
        return

    # Create a backup of the existing hyprland.lua file in the same directory
    try:
        backup_config = MAIN_CONFIG + ".bak"
        shutil.copy2(MAIN_CONFIG, backup_config)
        print(f"\033[92m[✓] Created a backup of your config at: {backup_config}\033[0m")
    except Exception as e:
        print(f"\033[91m[!] Warning: Failed to create a backup: {e}\033[0m")

    with open(MAIN_CONFIG, "r") as f:
        content = f.read()

    # 2. CHECK IF ALREADY SPLIT
    if "MODULAR CONFIGURATION IMPORTS" in content or (content.strip() and not re.search(r'hl\.(config|bind|monitor|exec)', content)):
        print("\033[93m[!] Notice: Your hyprland.lua file has already been split up!\033[0m")
        print("No split operations were performed to prevent overwriting your modular files.\n")
        print("If you want to start over or restore a default 'hyprland.lua' template, run this command:")
        print(f"\033[96mcurl -Lo ~/.config/hypr/hyprland.lua {DEFAULT_CONFIG_URL}\033[0m\n")

        choice = input("Would you like this script to overwrite your main file with the default template now? (y/N): ").strip().lower()
        if choice in ['y', 'yes']:
            download_default_config()
        else:
            print("Exiting.")
        return

    # 3. PROCEED TO PARSE AND SPLIT
    lines = content.splitlines(keepends=True)
    os.makedirs(CONFIGS_SUBDIR, exist_ok=True)

    sections = []
    current_section = None
    header_comment = []

    i = 0
    total_lines = len(lines)

    while i < total_lines:
        line = lines[i]
        stripped = line.strip()

        # Check if we hit a separator line of at least 4 dashes
        if re.match(r'^--[-]+$', stripped):
            if i + 1 < total_lines and "----" in lines[i+1]:
                title_line = lines[i+1].strip()
                title_clean = title_line.replace("--", "").strip("- ").strip()

                closing_idx = i + 2
                if closing_idx < total_lines and re.match(r'^--[-]+$', lines[closing_idx].strip()):

                    if current_section:
                        sections.append(current_section)

                    filename = clean_filename(title_clean) + ".lua"
                    current_section = {
                        "title": title_clean,
                        "filename": filename,
                        "content": [lines[i], lines[i+1], lines[closing_idx]]
                    }

                    i += 3
                    continue

        if current_section:
            current_section["content"].append(line)
        else:
            header_comment.append(line)

        i += 1

    if current_section:
        sections.append(current_section)

    if not sections:
        print("Error: No section headings matched. Config file was not modified.")
        return

    new_main_content = []
    for line in header_comment:
        if line.strip() and not re.match(r'^--[-]+$', line.strip()) and "----" not in line:
            new_main_content.append(line)

    if new_main_content and not new_main_content[-1].endswith("\n"):
        new_main_content.append("\n")

    new_main_content.append("-- =============================================================================\n")
    new_main_content.append("-- MODULAR CONFIGURATION IMPORTS\n")
    new_main_content.append("-- =============================================================================\n\n")

    for sec in sections:
        file_path = os.path.join(CONFIGS_SUBDIR, sec["filename"])
        content_str = "".join(sec["content"])

        # Scope fix: Convert 'local' config variables to globals across all files
        content_str = re.sub(
            r'^local\s+(mainMod|terminal|fileManager|menu|browser)\s*=',
            r'\1 =',
            content_str,
            flags=re.MULTILINE
        )

        with open(file_path, "w") as sf:
            sf.write(content_str)
        print(f"Created: {file_path}")

        module_path = f"configs/{sec['filename'].replace('.lua', '')}"
        new_main_content.append(f'require("{module_path}")\n')

    with open(MAIN_CONFIG, "w") as f:
        f.writelines(new_main_content)

    print(f"\nSuccessfully split config! Updated {MAIN_CONFIG}")

if __name__ == "__main__":
    split_config()
