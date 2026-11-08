# HH LOANHUB — Hybrid Loan Management Architecture (Phase 0)

> **Lead Infrastructure Architecture Specification**  
> **Phase 0 Objective:** Hybrid Deployment & Local-to-Cloud Pipeline. (Core business logic, loan databases, and bots will be introduced in subsequent phases).

---

## 1. Architectural Overview

```
+-----------------------------------------------------------------------------------+
|                                 CLIENT LAYER                                      |
|            Web Browser / Mobile App (Accesses Render Gateway Domain)              |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | HTTPS (Public Web Traffic)
                                          v
+-----------------------------------------------------------------------------------+
|                        RENDER CLOUD GATEWAY (Free Tier)                           |
|       Lightweight Nginx Alpine Container serving static UI + Reverse Proxy        |
|                                                                                   |
|  * Serves:  ui/* (Static Assets, Status Dashboard)                                |
|  * Proxies: /api/*  ----->  ${CLOUDFLARE_TUNNEL_URL}/api/*                        |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Zero-Trust Encrypted Tunnel (Outbound)
                                          v
+-----------------------------------------------------------------------------------+
|                            CLOUDFLARE TUNNEL                                      |
|    No router port-forwarding, no static IP required; secures traffic to localhost |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Local HTTP (0.0.0.0:8000)
                                          v
+-----------------------------------------------------------------------------------+
|                     LOCAL SECURE CORE ENGINE (Windows PC)                         |
|                                                                                   |
|  * run_server.py: FastAPI Core Engine + Heartbeat Telemetry                       |
|  * data/:         Strictly local SQLite/JSON databases (never pushed to Git)      |
|  * scripts/:      Windows batch automation & background runners                   |
+-----------------------------------------+-----------------------------------------+
                                          |
                                          | Automated Sync / Backup
                                          v
+-----------------------------------------------------------------------------------+
|                       GOOGLE DRIVE ZERO-LOSS STORAGE                              |
|           Automated timestamped snapshots of local `data/` directory              |
+-----------------------------------------------------------------------------------+
```

---

## 2. Directory Structure

```
hh-loanhub/
│
├── api/                             # Future modular FastAPI route handlers
│   └── .gitkeep
├── core/                            # Future core configs, security & bot engines
│   └── .gitkeep
├── data/                            # Strictly local SQLite/JSON storage (Git ignored)
│   └── .gitkeep
├── ui/                              # Static frontend assets
│   └── index.html                   # Dark-mode System Status Dashboard
├── scripts/                         # Automation & runner scripts
│   ├── backup_to_gdrive.bat         # Timestamped data backup to Google Drive
│   ├── push_to_github.bat           # Automated Git CI/CD commit & push
│   ├── run_background_service.vbs   # Silent Windows background runner (zero windows)
│   ├── start_local_engine.bat       # Starts local FastAPI server (run_server.py)
│   ├── start_remote_tunnel.bat      # Launches Cloudflare Tunnel to port 8000
│   └── stop_background_service.bat  # Cleanly terminates background processes
│
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules (protects data/ and secrets)
├── Dockerfile                       # Render gateway Nginx container definition
├── entrypoint.sh                    # Gateway container startup & env substitution
├── nginx.conf.template              # Nginx reverse proxy configuration template
├── render.yaml                      # Render Infrastructure as Code Blueprint
├── requirements.txt                 # Python dependencies
└── run_server.py                    # Local FastAPI Core Engine
```

---

## 3. Quickstart & Testing Guide

### Step 1: Set Up Python Environment Locally
```cmd
cd C:\Users\Wonderboom\.gemini\antigravity\scratch\hh-loanhub

:: 1. Create a virtual environment
python -m venv venv

:: 2. Activate virtual environment
venv\Scripts\activate

:: 3. Install dependencies
pip install -r requirements.txt

:: 4. Copy environment template
copy .env.example .env
```

### Step 2: Start and Test the Local Server
```cmd
:: Option A: Run directly in terminal
python run_server.py

:: Option B: Run via batch script
scripts\start_local_engine.bat
```
Open your browser to:
- **Local Dashboard:** [http://localhost:8000](http://localhost:8000)
- **Health API:** [http://localhost:8000/api/health](http://localhost:8000/api/health)
- **Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

The UI will immediately display a glowing green badge: **"Connected to Local Engine"**.

---

### Step 3: Launch Cloudflare Tunnel
In a new terminal (or using the script):
```cmd
scripts\start_remote_tunnel.bat
```
Cloudflare will output a public tunnel URL (e.g., `https://random-words.trycloudflare.com`).  
Test it in your browser: `https://<your-tunnel-url>/api/health`.

---

### Step 4: Deploy Cloud Gateway on Render (Free Tier)
1. Push your repository to GitHub using:
   ```cmd
   scripts\push_to_github.bat
   ```
2. In the [Render Dashboard](https://dashboard.render.com):
   - Click **New** -> **Blueprint**.
   - Connect your `hh-loanhub` repository. Render detects `render.yaml`.
   - Set the `CLOUDFLARE_TUNNEL_URL` environment variable to your tunnel address (e.g., `https://random-words.trycloudflare.com`).
   - Click **Apply**.
3. Render builds and launches the lightweight Nginx gateway. Open your Render URL:
   - The UI loads from Render's cloud CDN.
   - It proxies `/api/health` across the Cloudflare Tunnel directly to your Windows PC!
   - You will see the glowing green **"Connected to Local Engine"** badge live on the cloud.

---

### Step 5: Silent Windows Background Service
To run the server and tunnel in the background with zero visible command prompts:
- Double-click `scripts\run_background_service.vbs`.
- To make it start automatically when Windows boots:
  1. Press `Win + R`, type `shell:startup`, and press Enter.
  2. Right-click `scripts\run_background_service.vbs` -> **Create Shortcut**.
  3. Drag the shortcut into your Windows Startup folder.
- To stop all background services at any time, run `scripts\stop_background_service.bat`.

---

### Step 6: Google Drive Zero-Loss Backups
Run `scripts\backup_to_gdrive.bat` before making updates or schedule it via Windows Task Scheduler. It creates a snapshot under your configured Google Drive folder (`backup_YYYY-MM-DD_HH-MM-SS`) and mirrors the `latest/` directory.
