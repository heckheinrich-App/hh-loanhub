"""
HH LOANHUB - Local Core Engine
Phase 0: Hybrid Deployment Architecture & Secure Local Host

This server runs locally on your Windows PC. It serves the /api/* endpoints,
hosts the local SQLite/JSON databases in data/, and serves the static UI for
local development preview. In production, Render's Gateway reverse-proxies
public requests to this engine through a Cloudflare Tunnel.
"""

import os
import sys
import platform
import socket
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
from dotenv import load_dotenv

# Load local environment configuration
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = "0.0.0.0"
ENV_MODE = os.getenv("ENV", "development")

# Initialize FastAPI application
app = FastAPI(
    title="HH LOANHUB - Local Core Engine",
    description="Secure Core Engine, Database Host, and Cloudflare Tunnel Upstream Endpoint",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS)
# Allows seamless communication from Render Gateway, Cloudflare Tunnel, and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# API Endpoints
# (Must be defined BEFORE mounting static files at root "/")
# ------------------------------------------------------------------------------

@app.get("/api/health")
def health_check():
    """
    Heartbeat and connectivity verification endpoint.
    Used by the frontend dashboard and Render Gateway to confirm
    that the local Windows PC engine is reachable and online.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "online",
        "app": "HH LOANHUB",
        "engine": "Local Windows PC",
        "timestamp": now_iso
    }

@app.get("/api/system/status")
def system_status():
    """
    Detailed hardware and runtime telemetry for Phase 0 diagnostics.
    """
    return {
        "app": "HH LOANHUB",
        "status": "online",
        "engine": "Local Windows PC",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": ENV_MODE,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python_version": sys.version.split()[0],
            "hostname": socket.gethostname(),
        },
        "storage": {
            "data_directory": str(BASE_DIR / "data"),
            "data_dir_exists": (BASE_DIR / "data").exists()
        }
    }

# ------------------------------------------------------------------------------
# Mount Static Frontend
# ------------------------------------------------------------------------------
UI_DIR = BASE_DIR / "ui"
if UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
else:
    print(f"[WARNING] UI directory not found at {UI_DIR}")

# ------------------------------------------------------------------------------
# Main Execution Entrypoint
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 70)
    print("  HH LOANHUB - LOCAL CORE ENGINE STARTING")
    print("=" * 70)
    print(f"  * Local UI:       http://localhost:{PORT}")
    print(f"  * Health API:     http://localhost:{PORT}/api/health")
    print(f"  * Swagger Docs:   http://localhost:{PORT}/docs")
    print(f"  * Network Bind:   http://{HOST}:{PORT}")
    print(f"  * Environment:    {ENV_MODE}")
    print("=" * 70)
    print("  Press Ctrl+C to stop the server.")
    print("=" * 70)

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
