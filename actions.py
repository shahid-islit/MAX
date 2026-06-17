import subprocess
import os
import json
from app_scanner import scan_apps, find_app, rescan

# Load app map on startup (uses cache if available)
_APP_MAP = scan_apps()

# ─── UWP / WINDOWS STORE APPS ─────────────────────────────────────────────────
# These apps have no .exe in Program Files — Windows launches them via URI scheme

UWP_MAP = {
    "microsoft store": "ms-windows-store:",
    "store": "ms-windows-store:",
    "netflix": "netflix:",
    "whatsapp": "whatsapp:",
    "spotify": "spotify:",
    "mail": "outlookmail:",
    "calendar": "outlookcal:",
    "photos": "ms-photos:",
    "settings": "ms-settings:",
    "calculator": "calculator:",
    "xbox": "xbox:",
    "prime video": "primevideo:",
}

# ─── APP LAUNCHER ─────────────────────────────────────────────────────────────

def open_app(app_name: str) -> str:
    key = app_name.lower().strip()

    # 1. Check UWP map first — exact match Windows Store apps
    for uwp_name, uri in UWP_MAP.items():
        if key == uwp_name or key in uwp_name or uwp_name in key:
            try:
                os.startfile(uri)
                return f"Opening {app_name}."
            except Exception as e:
                return f"Couldn't open {app_name}: {e}"

    # 2. Fall through to scanned .exe apps
    path = find_app(key, _APP_MAP)
    if path:
        # Safeguard: only launch actual executables, not images or documents
        ext = os.path.splitext(path)[1].lower()
        if ext not in {".exe", ".lnk"}:
            return f"I found a file named '{app_name}' but it doesn't look like an app. Try being more specific."
        try:
            subprocess.Popen(f'"{path}"', shell=True)
            return f"Opening {app_name}."
        except Exception as e:
            return f"Found {app_name} but couldn't open it: {e}"

    return f"I couldn't find '{app_name}' on your system. If you just installed it, say 'rescan apps' and I'll look again."

def rescan_apps() -> str:
    global _APP_MAP
    result = rescan()
    _APP_MAP = scan_apps()
    return result

# ─── BROWSER / WEB ────────────────────────────────────────────────────────────

SITE_MAP = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "netflix": "https://www.netflix.com",
    "twitter": "https://www.twitter.com",
    "x": "https://www.x.com",
    "instagram": "https://www.instagram.com",
    "reddit": "https://www.reddit.com",
    "notion": "https://www.notion.so",
    "figma": "https://www.figma.com",
    "chatgpt": "https://chat.openai.com",
    "claude": "https://claude.ai",
}

def open_website(site: str) -> str:
    key = site.lower().strip()
    url = SITE_MAP.get(key)
    if not url:
        if "." in site and " " not in site:
            url = f"https://{site}" if not site.startswith("http") else site
        else:
            query = site.replace(" ", "+")
            url = f"https://www.google.com/search?q={query}"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    subprocess.Popen(f'"{chrome_path}" "{url}"', shell=True)
    return f"Opening {url}."

# ─── REGISTERED FOLDERS ───────────────────────────────────────────────────────

FOLDERS_FILE = os.path.join(os.path.dirname(__file__), "registered_folders.json")

def _load_folders() -> dict:
    if not os.path.exists(FOLDERS_FILE):
        return {}
    with open(FOLDERS_FILE, "r") as f:
        return json.load(f)

def _save_folders(folders: dict):
    with open(FOLDERS_FILE, "w") as f:
        json.dump(folders, f, indent=2)

def register_folder(name: str, path: str) -> str:
    path = path.strip().strip('"').strip("'")
    if not os.path.exists(path):
        return f"That path doesn't exist: {path}"
    folders = _load_folders()
    folders[name.lower()] = path
    _save_folders(folders)
    return f"Got it. I've registered '{name}' -> {path}"

def open_registered_folder(name: str) -> str:
    folders = _load_folders()
    key = name.lower()
    if key not in folders:
        matches = [k for k in folders if key in k or k in key]
        if not matches:
            return f"I don't have a folder registered as '{name}'. Tell me the path and I'll remember it."
        key = matches[0]
    path = folders[key]
    os.startfile(path)
    return f"Opening {key} folder."

def open_file_in_folder(folder_name: str, filename: str) -> str:
    folders = _load_folders()
    key = folder_name.lower()
    if key not in folders:
        return f"No folder registered as '{folder_name}'."
    folder_path = folders[key]
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            if filename.lower() in f.lower():
                full_path = os.path.join(root, f)
                os.startfile(full_path)
                return f"Opening {f}"
    return f"Couldn't find '{filename}' in your {folder_name} folder."

def list_registered_folders() -> str:
    folders = _load_folders()
    if not folders:
        return "No folders registered yet."
    lines = [f"* {name}: {path}" for name, path in folders.items()]
    return "Registered folders:\n" + "\n".join(lines)