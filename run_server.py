"""
HH LOANHUB / HH Cash Solutions - Local Core Engine
Phase 1: Hybrid Architecture, Full Authentication, Loan Engine & PWA Host
"""

import os
import sys
import platform
import socket
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx
from dotenv import load_dotenv

# Database & Routers
from core.database import init_db, DB_PATH
from core.scheduler import loan_lifecycle_monitor_worker
from api.auth import router as auth_router
from api.loans import router as loans_router
from api.admin import router as admin_router

# Load local environment configuration
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuration
PORT = int(os.getenv("PORT", "8000"))
HOST = "0.0.0.0"
ENV_MODE = os.getenv("ENV", "development")
RENDER_GATEWAY_URL = os.getenv("RENDER_GATEWAY_URL", "https://hh-loanhub-gateway.onrender.com").rstrip("/")


# ------------------------------------------------------------------------------
# Render Gateway Free-Tier Keep-Alive Worker
# ------------------------------------------------------------------------------
async def render_keep_alive_worker():
    """Background task that pings the Render gateway while the local PC is online."""
    await asyncio.sleep(20)  # Warmup wait
    print(f"[KEEP-ALIVE] Background Render keep-alive pinger activated -> {RENDER_GATEWAY_URL}")
    while True:
        try:
            target = f"{RENDER_GATEWAY_URL}/api/health"
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(target)
                if res.status_code == 200:
                    print(f"[KEEP-ALIVE] Ping successful: {target} (200 OK)")
                else:
                    print(f"[KEEP-ALIVE] Ping status: {res.status_code}")
        except Exception as e:
            print(f"[KEEP-ALIVE] Notice: {e}")
        await asyncio.sleep(600)  # Ping every 10 minutes (Render spins down after 15 mins)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database and tables
    init_db()
    # Startup: spawn keep-alive and loan lifecycle background workers
    keep_alive_task = asyncio.create_task(render_keep_alive_worker())
    scheduler_task = asyncio.create_task(loan_lifecycle_monitor_worker())
    yield
    # Shutdown
    keep_alive_task.cancel()
    scheduler_task.cancel()


# Initialize FastAPI application
app = FastAPI(
    title="HH Cash Solutions - Core Engine",
    description="Loan Management Engine, SQLite Database Host, and Cloudflare Tunnel Upstream Endpoint",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enforce Strict No-Cache Headers on All Responses (HTML, JS, CSS, JSON)
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ------------------------------------------------------------------------------
# Register Core API Routers
# ------------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(loans_router)
app.include_router(admin_router)


# ------------------------------------------------------------------------------
# System Endpoints
# ------------------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    """Heartbeat endpoint for frontend telemetry and Render reverse-proxy checks."""
    now_iso = datetime.now(timezone.utc).isoformat()
    return {
        "status": "online",
        "app": "HH Cash Solutions",
        "engine": "Local Windows PC",
        "timestamp": now_iso
    }


@app.get("/api/system/status")
def system_status():
    """Hardware and database status diagnostics."""
    return {
        "app": "HH Cash Solutions",
        "status": "online",
        "engine": "Local Windows PC",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": ENV_MODE,
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "python_version": sys.version.split()[0],
            "hostname": socket.gethostname(),
        },
        "database": {
            "path": str(DB_PATH),
            "exists": DB_PATH.exists()
        },
        "gateway": {
            "render_url": RENDER_GATEWAY_URL,
            "keep_alive_interval": "600s"
        }
    }


# ------------------------------------------------------------------------------
# Mount Static Frontend (Must be mounted AFTER API endpoints)
# ------------------------------------------------------------------------------
UI_DIR = BASE_DIR / "ui"
if UI_DIR.exists():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
else:
    print(f"[WARNING] UI directory not found at {UI_DIR}")


if __name__ == "__main__":
    print("=" * 70)
    print("  HH CASH SOLUTIONS - LOCAL CORE ENGINE STARTING")
    print("=" * 70)
    print(f"  * Local UI:       http://localhost:{PORT}")
    print(f"  * Health API:     http://localhost:{PORT}/api/health")
    print(f"  * Swagger Docs:   http://localhost:{PORT}/docs")
    print(f"  * Network Bind:   http://{HOST}:{PORT}")
    print(f"  * Environment:    {ENV_MODE}")
    print(f"  * Database:       {DB_PATH}")
    print(f"  * Render Gateway: {RENDER_GATEWAY_URL}")
    print("=" * 70)
    print("  Press Ctrl+C to stop the server.")
    print("=" * 70)

    uvicorn.run(app, host=HOST, port=PORT, log_level="info")
