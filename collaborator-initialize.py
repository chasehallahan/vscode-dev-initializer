import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

from modules import comment_cleaner

HERE = Path(__file__).parent.resolve()
EXT_FILE = HERE / "assets" / "vscode-extensions.txt"
VS_SETTINGS_FILE = HERE / "assets" / "settings.json"
PS_PROFILE = HERE / "assets" / "Microsoft.PowerShell_profile.ps1"
FONTS = HERE / "assets" / "font"

USER_SETTINGS_FILE = Path(os.environ["APPDATA"]) / "Code" / "User" / "settings.json"
USER_PS_PROFILE = (
    Path(os.environ["LOCALAPPDATA"]) / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
)
USER_FONTS = Path(os.environ["LOCALAPPDATA"]) / "Microsoft" / "Windows" / "Fonts"


# ─────────────────────────────────────────────────
# Create or update .vscode/settings.json
#     - Ensures local environment activation
#     - Merges in project-level settings
#     - Adds PS $PROFILE for venv activated note
# ─────────────────────────────────────────────────
print("\n🛠  Updating VS Code settings.json...\n")

# Create or open .vscode settings and load
if not VS_SETTINGS_FILE.parent.exists():
    print("⚠️  No existing VS Code settings. Creating a new one.")
    VS_SETTINGS_FILE.parent.mkdir(parents=True)

try:
    if (
        not VS_SETTINGS_FILE.exists()
        or not VS_SETTINGS_FILE.read_text(encoding="utf-8").strip()
    ):
        raise json.JSONDecodeError("Empty or missing file", "", 0)

    with VS_SETTINGS_FILE.open("r", encoding="utf-8") as f:
        o = comment_cleaner(f)
        current_settings = json.load(o)

except json.JSONDecodeError:
    print("⚠️ .vscode/settings.json is missing, empty, or invalid. Replacing it.\n")
    VS_SETTINGS_FILE.write_text("{}", encoding="utf-8")
    current_settings = {}

# Merge with new settings
try:
    with USER_SETTINGS_FILE.open("r+", encoding="utf-8") as f:
        new_settings = json.load(comment_cleaner(f))
except json.JSONDecodeError:
    USER_SETTINGS_FILE.write_text("{}", encoding="utf-8")
    new_settings = {}
USER_SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
merged = {**new_settings, **current_settings}
with USER_SETTINGS_FILE.open("w", encoding="utf-8") as f:
    json.dump(merged, f, indent=4)

# Write updated settings
with VS_SETTINGS_FILE.open("r+", encoding="utf-8") as f:
    json.dump(current_settings, f, indent=4)

print("✅ VS Code settings updated.")

# Add fonts for terminal
USER_FONTS.mkdir(parents=True, exist_ok=True)
for font in FONTS.glob("*.ttf"):
    dst = USER_FONTS / font.name
    if not dst.exists():
        try:
            shutil.copy2(font, dst)
        except PermissionError:
            print(f"❌ Error: Couldn't add {font} to user fonts at {USER_FONTS}")

# Add Microsoft.PowerShell_profile.ps1 to user
USER_PS_PROFILE.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(PS_PROFILE, USER_PS_PROFILE)

# ─────────────────────────────────────────────────
# Install VS Code extensions listed in assets/
#     - Skips comments and blank lines
#     - Cleans extension names for display
#     - Checks for availability of `code` CLI
# ─────────────────────────────────────────────────
if not EXT_FILE.exists():
    print(f"\n❌ Error: {EXT_FILE} not found.")
    sys.exit(1)

print("\n📦 Installing VS Code extensions...\n")
code_cli = shutil.which("code") or shutil.which("code.cmd")
if not code_cli:
    print("⚠️ VS Code CLI ('code') not found. Skipping extension installs.\n")
else:
    installed_ext = set(
        subprocess.run(
            [code_cli, "--list-extensions"], capture_output=True, text=True, check=True
        ).stdout.splitlines()
    )

    with EXT_FILE.open() as f:
        for line in f:
            ext = line.split("#", 1)[0].strip()
            if not ext:
                continue
            if ext in installed_ext:
                print(f"⏭ Already installed: {ext}")
                continue

            _clean_ext = ext.split(".", 1)[-1]
            print(f"➡ Installing: {_clean_ext}")
            result = subprocess.run(
                f"code --install-extension {ext} --force",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )

            if result.returncode == 0:
                print(f"✅ Installed: {_clean_ext}")
            else:
                print(f"❌ Failed to install extension {_clean_ext}:\n{result.stderr}")

print(
    "\n🎉 All done! Please reopen VS Code to apply changes. You can use Ctrl+Shift+P → Reload Window.\n"
)
