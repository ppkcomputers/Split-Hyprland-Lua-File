#!/usr/bin/env python3
import os
import re
import shutil
import sys
import urllib.request

# Determine the config directory universally (honors XDG_CONFIG_HOME, defaults to ~/.config)
XDG_CONFIG_DIR = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))[cite: 2]
HYPR_DIR = os.path.join(XDG_CONFIG_DIR, "hypr")[cite: 2]
MAIN_CONFIG = os.path.join(HYPR_DIR, "hyprland.lua")[cite: 2]
CONFIGS_SUBDIR = os.path.join(HYPR_DIR, "configs")[cite: 2]

# Official default template URL directly from the Hyprland upstream repository
DEFAULT_CONFIG_URL = "https://raw.githubusercontent.com/hyprwm/Hyprland/main/example/hyprland.lua"[cite: 2]

def clean_filename(title):
    # Strip any leading/trailing dashes and spaces from the title
    cleaned = title.strip("-").strip()[cite: 2]
    # Replace spaces or symbols with underscores
    cleaned = re.sub(r'[\(\)\-\/]', '_', cleaned)[cite: 2]
    cleaned = re.sub(r'\s+', '_', cleaned)[cite: 2]
    cleaned = re.sub(r'_+', '_', cleaned)[cite: 2]
    return cleaned.lower().strip("_")[cite: 2]

def download_default_config():
    print(f"\nCreating directory: {HYPR_DIR}")[cite: 2]
    os.makedirs(HYPR_DIR, exist_ok=True)[cite: 2]

    print("Downloading official default hyprland.lua template...")[cite: 2]
    try:
        # Download the file natively using Python's standard library
        urllib.request.urlretrieve(DEFAULT_CONFIG_URL, MAIN_CONFIG)[cite: 2]
        print(f"\033[92m[✓] Successfully downloaded default template to {MAIN_CONFIG}!\033[0m")[cite: 2]
        print("You can now run this script again to split your newly downloaded config.")[cite: 2]
    except Exception as e:
        print(f"\033[91m[!] Error downloading file: {e}\033[0m")[cite: 2]

def split_config():
    # 1. CHECK IF FILE EXISTS
    if not os.path.exists(MAIN_CONFIG):[cite: 2]
        print(f"\033[91m[!] Error: Could not find main config at {MAIN_CONFIG}\033[0m")[cite: 2]
        print("\nIf you want to download a default 'hyprland.lua' template manually, run this command:")[cite: 2]
        print(f"\033[96mcurl -Lo ~/.config/hypr/hyprland.lua {DEFAULT_CONFIG_URL}\033[0m\n")[cite: 2]

        # Interactive prompt to download automatically
        choice = input("Would you like this script to download the default template for you now? (y/N): ").strip().lower()[cite: 2]
        if choice in ['y', 'yes']:[cite: 2]
            download_default_config()[cite: 2]
        else:[cite: 2]
            print("Exiting.")[cite: 2]
        return[cite: 2]

    # Create a backup of the existing hyprland.lua file in the same directory
    try:
        backup_config = MAIN_CONFIG + ".bak"
        shutil.copy2(MAIN_CONFIG, backup_config)
        print(f"\033[92m[✓] Created a backup of your config at: {backup_config}\033[0m")
    except Exception as e:
        print(f"\033[91m[!] Warning: Failed to create a backup: {e}\033[0m")

    with open(MAIN_CONFIG, "r") as f:[cite: 2]
        content = f.read()[cite: 2]

    # 2. CHECK IF ALREADY SPLIT
    if "MODULAR CONFIGURATION IMPORTS" in content or (content.strip() and not re.search(r'hl\.(config|bind|monitor|exec)', content)):[cite: 2]
        print("\033[93m[!] Notice: Your hyprland.lua file has already been split up!\033[0m")[cite: 2]
        print("No split operations were performed to prevent overwriting your modular files.\n")[cite: 2]
        print("If you want to start over or restore a default 'hyprland.lua' template, run this command:")[cite: 2]
        print(f"\033[96mcurl -Lo ~/.config/hypr/hyprland.lua {DEFAULT_CONFIG_URL}\033[0m\n")[cite: 2]

        choice = input("Would you like this script to overwrite your main file with the default template now? (y/N): ").strip().lower()[cite: 2]
        if choice in ['y', 'yes']:[cite: 2]
            download_default_config()[cite: 2]
        else:[cite: 2]
            print("Exiting.")[cite: 2]
        return[cite: 2]

    # 3. PROCEED TO PARSE AND SPLIT
    lines = content.splitlines(keepends=True)[cite: 2]
    os.makedirs(CONFIGS_SUBDIR, exist_ok=True)[cite: 2]

    sections = [][cite: 2]
    current_section = None[cite: 2]
    header_comment = [][cite: 2]

    i = 0[cite: 2]
    total_lines = len(lines)[cite: 2]

    while i < total_lines:[cite: 2]
        line = lines[i][cite: 2]
        stripped = line.strip()[cite: 2]

        # Check if we hit a separator line of at least 4 dashes
        if re.match(r'^--[-]+$', stripped):[cite: 2]
            if i + 1 < total_lines and "----" in lines[i+1]:[cite: 2]
                title_line = lines[i+1].strip()[cite: 2]
                title_clean = title_line.replace("--", "").strip("- ").strip()[cite: 2]

                closing_idx = i + 2[cite: 2]
                if closing_idx < total_lines and re.match(r'^--[-]+$', lines[closing_idx].strip()):[cite: 2]

                    if current_section:[cite: 2]
                        sections.append(current_section)[cite: 2]

                    filename = clean_filename(title_clean) + ".lua"[cite: 2]
                    current_section = {
                        "title": title_clean,
                        "filename": filename,
                        "content": [lines[i], lines[i+1], lines[closing_idx]]
                    }[cite: 2]

                    i += 3[cite: 2]
                    continue[cite: 2]

        if current_section:[cite: 2]
            current_section["content"].append(line)[cite: 2]
        else:[cite: 2]
            header_comment.append(line)[cite: 2]

        i += 1[cite: 2]

    if current_section:[cite: 2]
        sections.append(current_section)[cite: 2]

    if not sections:[cite: 2]
        print("Error: No section headings matched. Config file was not modified.")[cite: 2]
        return[cite: 2]

    new_main_content = [][cite: 2]
    for line in header_comment:[cite: 2]
        if line.strip() and not re.match(r'^--[-]+$', line.strip()) and "----" not in line:[cite: 2]
            new_main_content.append(line)[cite: 2]

    if new_main_content and not new_main_content[-1].endswith("\n"):[cite: 2]
        new_main_content.append("\n")[cite: 2]

    new_main_content.append("-- =============================================================================\n")[cite: 2]
    new_main_content.append("-- MODULAR CONFIGURATION IMPORTS\n")[cite: 2]
    new_main_content.append("-- =============================================================================\n\n")[cite: 2]

    for sec in sections:[cite: 2]
        file_path = os.path.join(CONFIGS_SUBDIR, sec["filename"])[cite: 2]
        content_str = "".join(sec["content"])[cite: 2]

        # Scope fix: Convert 'local' config variables to globals across all files
        content_str = re.sub(
            r'^local\s+(mainMod|terminal|fileManager|menu|browser)\s*=',[cite: 2]
            r'\1 =',[cite: 2]
            content_str,[cite: 2]
            flags=re.MULTILINE[cite: 2]
        )

        with open(file_path, "w") as sf:[cite: 2]
            sf.write(content_str)[cite: 2]
        print(f"Created: {file_path}")[cite: 2]

        module_path = f"configs/{sec['filename'].replace('.lua', '')}"[cite: 2]
        new_main_content.append(f'require("{module_path}")\n')[cite: 2]

    with open(MAIN_CONFIG, "w") as f:[cite: 2]
        f.writelines(new_main_content)[cite: 2]

    print(f"\nSuccessfully split config! Updated {MAIN_CONFIG}")[cite: 2]

if __name__ == "__main__":
    split_config()[cite: 2]
