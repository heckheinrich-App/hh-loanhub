"""
HH LOANHUB - Cloudflare Tunnel Synchronizer & Dynamic Config Engine
Phase 0: Hybrid Deployment Architecture

This script:
1. Locates and spawns `cloudflared tunnel --url http://localhost:8000`.
2. Monitors process output to capture the public `https://*.trycloudflare.com` URL.
3. Automatically writes the captured URL into `ui/tunnel_config.json`.
4. Updates `CLOUDFLARE_TUNNEL_URL` in `.env`.
5. Logs tunnel events to `data/tunnel.log` and writes `data/latest_tunnel_url.txt`.
6. Automatically commits and pushes `ui/tunnel_config.json` to GitHub (if a Git remote exists).
7. Keeps running in the background to maintain the tunnel alive.
"""

import os
import sys
import re
import json
import time
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
UI_DIR = BASE_DIR / "ui"
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = UI_DIR / "tunnel_config.json"
ENV_FILE = BASE_DIR / ".env"
LOG_FILE = DATA_DIR / "tunnel.log"
URL_FILE = DATA_DIR / "latest_tunnel_url.txt"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
UI_DIR.mkdir(parents=True, exist_ok=True)


def find_cloudflared() -> str:
    """Finds cloudflared executable in PATH or WinGet packages."""
    binary = shutil.which("cloudflared")
    if binary:
        return binary

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pkg_dir = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkg_dir.exists():
            for cf_dir in winget_pkg_dir.glob("Cloudflare.cloudflared*"):
                candidate = cf_dir / "cloudflared.exe"
                if candidate.exists():
                    return str(candidate)

    # Standard program files fallback
    fallback = Path("C:/Program Files/cloudflared/cloudflared.exe")
    if fallback.exists():
        return str(fallback)

    return "cloudflared"


def find_git() -> str:
    """Finds git executable in PATH or WinGet packages."""
    binary = shutil.which("git")
    if binary:
        return binary

    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_pkg_dir = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        if winget_pkg_dir.exists():
            for g_dir in winget_pkg_dir.glob("Git.MinGit*"):
                candidate = g_dir / "cmd" / "git.exe"
                if candidate.exists():
                    return str(candidate)
            for g_dir in winget_pkg_dir.glob("Git.Git*"):
                candidate = g_dir / "cmd" / "git.exe"
                if candidate.exists():
                    return str(candidate)
    return "git"


def update_env_file(tunnel_url: str):
    """Updates or sets CLOUDFLARE_TUNNEL_URL in .env."""
    lines = []
    found = False
    if ENV_FILE.exists():
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

    new_lines = []
    for line in lines:
        if line.strip().startswith("CLOUDFLARE_TUNNEL_URL="):
            new_lines.append(f"CLOUDFLARE_TUNNEL_URL={tunnel_url}\n")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"\n# Auto-updated Cloudflare Tunnel URL\nCLOUDFLARE_TUNNEL_URL={tunnel_url}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


def write_tunnel_config(tunnel_url: str):
    """Writes the active tunnel URL and metadata into ui/tunnel_config.json."""
    data = {
        "tunnel_url": tunnel_url,
        "api_url": f"{tunnel_url}/api",
        "health_url": f"{tunnel_url}/api/health",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "online",
        "provider": "Cloudflare Zero Trust Quick Tunnel"
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    with open(URL_FILE, "w", encoding="utf-8") as f:
        f.write(tunnel_url)

    update_env_file(tunnel_url)
    print(f"[SYNC] Successfully updated config: {CONFIG_FILE}")
    print(f"[SYNC] Active Tunnel: {tunnel_url}")


def git_push_config():
    """Automatically commits and pushes ui/tunnel_config.json if a remote exists."""
    git_bin = find_git()
    try:
        # Check if remote origin exists
        result = subprocess.run([git_bin, "remote", "get-url", "origin"], cwd=str(BASE_DIR), capture_output=True, text=True)
        if result.returncode != 0:
            print("[GIT] No remote origin configured yet. Skipping auto-push to GitHub.")
            return

        print("[GIT] Staging ui/tunnel_config.json...")
        subprocess.run([git_bin, "add", "ui/tunnel_config.json"], cwd=str(BASE_DIR), check=True)

        commit_msg = f"chore(infra): sync active cloudflare tunnel url [{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC]"
        subprocess.run([git_bin, "commit", "-m", commit_msg], cwd=str(BASE_DIR), capture_output=True)

        print("[GIT] Pushing updated tunnel config to GitHub (origin/main)...")
        push_res = subprocess.run([git_bin, "push", "origin", "main"], cwd=str(BASE_DIR), capture_output=True, text=True)
        if push_res.returncode == 0:
            print("[GIT] Successfully pushed new tunnel config to GitHub!")
        else:
            print(f"[GIT] Push notice: {push_res.stderr.strip() or push_res.stdout.strip()}")
    except Exception as e:
        print(f"[GIT] Auto-push notice: {e}")


def run_tunnel():
    """Spawns cloudflared, streams output, captures URL, and keeps tunnel running."""
    cf_bin = find_cloudflared()
    print("=" * 70)
    print("  HH LOANHUB - CLOUDFLARE TUNNEL SYNCHRONIZER")
    print("=" * 70)
    print(f"  * Binary: {cf_bin}")
    print(f"  * Target: http://localhost:8000")
    print(f"  * Output: {CONFIG_FILE}")
    print("=" * 70)

    cmd = [cf_bin, "tunnel", "--url", "http://localhost:8000"]

    with open(LOG_FILE, "a", encoding="utf-8") as log_fp:
        log_fp.write(f"\n--- Tunnel Session Started at {datetime.now(timezone.utc).isoformat()} ---\n")

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    try:
        for line in proc.stdout:
            # Mirror to data/tunnel.log
            with open(LOG_FILE, "a", encoding="utf-8") as log_fp:
                log_fp.write(line)

            if not tunnel_url:
                match = url_pattern.search(line)
                if match:
                    tunnel_url = match.group(0)
                    print(f"\n[FOUND] Captured Live Cloudflare Tunnel URL: {tunnel_url}")
                    write_tunnel_config(tunnel_url)
                    git_push_config()
                    print("\n[READY] Tunnel is active and proxying to http://localhost:8000.")
                    print("[INFO] Press Ctrl+C in this terminal to terminate the tunnel.\n")
                    sys.stdout.flush()

        proc.wait()
    except KeyboardInterrupt:
        print("\n[STOP] Terminating Cloudflare Tunnel...")
        proc.terminate()
        proc.wait()


if __name__ == "__main__":
    run_tunnel()
