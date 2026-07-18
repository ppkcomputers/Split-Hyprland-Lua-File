# Hyprland Lua Config Splitter

A Python utility designed to automatically parse, split, and modularize your monolithic `hyprland.lua` configuration file. 

It reads your main configuration file, extracts sections demarcated by dashed comment banners, writes them into individual files inside a subdirectory, and replaces your main configuration with clean, modular Lua `require()` statements.

---

## Run from terminal  

curl -fsSL https://raw.githubusercontent.com/ppkcomputers/Split-Hyprland-Lua-File/main/split-lua.py -o split-lua.py && chmod +x split-lua.py && ./split-lua.py  


## Features

* **Universal Path Detection:** Respects `XDG_CONFIG_HOME` and falls back seamlessly to `~/.config/hypr/`.
* **Automatic Template Downloader:** If you don't have a configuration file yet, the script offers to pull the official upstream `hyprland.lua` template for you natively[cite: 1].
* **Smart Duplication Guard:** Checks if your config is already modularized and prevents accidental overrides[cite: 1].
* **Clean Filename Generation:** Converts banner titles (e.g., `-- --- KEYBINDINGS --- --`) into standardized lowercase filenames (e.g., `keybindings.lua`)[cite: 1].
* **Global Scope Adjustment:** Automatically strips `local` declarations for key configuration variables so they are accessible across all your imported sub-modules[cite: 1].

---

## How It Works

1. **Checks for Main Config:** Looks for `~/.config/hypr/hyprland.lua`[cite: 1]. If missing, it prompts to download the default template[cite: 1].
2. **Parses Sections:** Uses dash-comment banners (like `-- -------------------`) to divide your configuration into logical sections[cite: 1].
3. **Generates Sub-files:** Saves each section as a separate `.lua` file inside `~/.config/hypr/configs/`[cite: 1].
4. **Links Everything:** Updates your main `hyprland.lua` to simply call `require("configs/section_name")` for each module[cite: 1].

---

## Installation & Setup

### 1. Make the Script Executable
Before running the script, you need to grant it execution permissions using `chmod`. Open your terminal and run:

```bash
chmod +x split-lua.py
