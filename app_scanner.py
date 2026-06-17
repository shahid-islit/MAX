import os
import json
from pathlib import Path

CACHE_FILE = os.path.join(os.path.dirname(__file__), "app_cache.json")

# ─── SAFEGUARD: ONLY THESE FOLDERS ARE EVER SCANNED ──────────────────────────
# MAX will NEVER write to, modify, or execute anything in these folders.
# Strictly read-only directory listing. No file creation, no script injection.

SCAN_LOCATIONS = [
    r"C:\Program Files",
    r"C:\Program Files (x86)",
    os.path.join(os.environ.get("APPDATA", ""), "Microsoft\Windows\Start Menu\Programs"),
    os.path.join(os.environ.get("USERPROFILE", ""), "Desktop"),
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData\Local"),
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData\Roaming"),
]

# ─── SAFEGUARD: BLACKLISTED PATHS — NEVER SCANNED ────────────────────────────
# Even if somehow referenced, MAX will skip these entirely.

BLACKLISTED_PATHS = [
    os.path.join(os.environ.get("USERPROFILE", ""), "AppData\Local\Temp"),
    r"C:\Windows",
    r"C:\Windows\System32",
    os.path.dirname(__file__),  # MAX's own folder — never scans itself
]

# Only scan .exe and .lnk files — nothing else
ALLOWED_EXTENSIONS = {".exe", ".lnk"}

# Skip folders with these names — they're never user-facing apps
SKIP_FOLDERS = {
    "temp", "tmp", "cache", "logs", "crash", "update", "uninstall",
    "redist", "vcredist", "directx", "dotnet", "__pycache__",
    "recent",
}
def _is_blacklisted(path: str) -> bool:
    path_lower = path.lower()
    for blocked in BLACKLISTED_PATHS:
        if path_lower.startswith(blocked.lower()):
            return True
    return False

def _clean_name(filename: str) -> str:
    """Turn 'Google Chrome.exe' into 'google chrome'"""
    name = os.path.splitext(filename)[0]
    return name.lower().strip()

def scan_apps(force_rescan: bool = False) -> dict:
    """
    Scan installed apps and return a dict of {app_name: exe_path}.
    Uses cache if available. Set force_rescan=True to rebuild.
    READ-ONLY — never modifies any scanned directory.
    """
    if not force_rescan and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)

    print("Scanning your system for apps... (one-time setup)")
    app_map = {}

    for base_path in SCAN_LOCATIONS:
        if not os.path.exists(base_path):
            continue
        if _is_blacklisted(base_path):
            continue

        try:
            for root, dirs, files in os.walk(base_path):
                # Safeguard: skip blacklisted paths mid-walk
                if _is_blacklisted(root):
                    dirs.clear()  # Don't recurse further
                    continue

                # Skip junk folders
                dirs[:] = [
                    d for d in dirs
                    if d.lower() not in SKIP_FOLDERS
                ]

                for filename in files:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in ALLOWED_EXTENSIONS:
                        continue

                    full_path = os.path.join(root, filename)
                    name = _clean_name(filename)

                    if name and name not in app_map:
                        app_map[name] = full_path

        except PermissionError:
            continue  # Skip folders we can't read — never force access

    # Save cache — only this file is ever written by the scanner
    with open(CACHE_FILE, "w") as f:
        json.dump(app_map, f, indent=2)

    print(f"Done. Found {len(app_map)} apps.")
    return app_map

def find_app(query: str, app_map: dict) -> str | None:
    """
    Fuzzy match a query against the app map.
    Returns the exe path if found, None otherwise.
    """
    query = query.lower().strip()

    # Exact match first
    if query in app_map:
        return app_map[query]

    # Starts-with match
    for name, path in app_map.items():
        if name.startswith(query):
            return path

    # Contains match
    for name, path in app_map.items():
        if query in name:
            return path

    # Abbreviation match — e.g. "nte" matches "neverness to everness"
    for name, path in app_map.items():
        initials = "".join(word[0] for word in name.split() if word)
        if query == initials:
            return path

    return None

def rescan(quietly: bool = False) -> str:
    """Force a fresh scan — call this when you install new apps."""
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
    app_map = scan_apps(force_rescan=True)
    return f"Rescanned. Found {len(app_map)} apps."