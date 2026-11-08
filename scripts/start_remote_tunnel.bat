@echo off
setlocal EnableDelayedExpansion

title HH LOANHUB - Cloudflare Remote Tunnel
cd /d "%~dp0\.."

echo ==============================================================================
echo              HH LOANHUB - CLOUDFLARE TUNNEL GATEWAY LAUNCHER
echo ==============================================================================
echo Local Upstream Target: http://localhost:8000
echo.

:: Check if cloudflared is installed (check PATH and WinGet install locations)
where cloudflared >nul 2>&1
if %ERRORLEVEL% neq 0 (
    for /d %%D in ("%LOCALAPPDATA%\Microsoft\WinGet\Packages\Cloudflare.cloudflared*") do (
        if exist "%%D\cloudflared.exe" set "PATH=%%D;!PATH!"
    )
)

where cloudflared >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] cloudflared.exe was not found in your system PATH.
    echo.
    echo To install Cloudflare Tunnel on Windows:
    echo   1. Download cloudflared from:
    echo      https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe
    echo   2. Rename to 'cloudflared.exe' and place in C:\Windows\System32 or add to PATH.
    echo   3. Alternatively with winget: winget install --id Cloudflare.cloudflared
    echo.
    pause
    exit /b 1
)

:: -----------------------------------------------------------------------------
:: TUNNEL CONFIGURATION
:: -----------------------------------------------------------------------------
:: Quick Ad-hoc Tunnel (Default for Phase 0 testing):
:: Generates a temporary public *.trycloudflare.com URL.
::
:: Production Named Tunnel:
:: Once you create a named tunnel in Cloudflare Zero Trust dashboard, set your token
:: either below or in your .env file as CLOUDFLARE_TUNNEL_TOKEN.
:: -----------------------------------------------------------------------------

set TUNNEL_TOKEN=

if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set KEY=%%A
        set VAL=%%B
        if /i "!KEY!"=="CLOUDFLARE_TUNNEL_TOKEN" (
            set TUNNEL_TOKEN=!VAL!
        )
    )
)

if defined TUNNEL_TOKEN (
    echo [MODE] Running Production Cloudflare Named Tunnel with Token...
    cloudflared tunnel run --token !TUNNEL_TOKEN!
) else (
    echo [MODE] Running Quick Ad-hoc Tunnel pointing to http://localhost:8000...
    echo [NOTE] Copy the generated https://*.trycloudflare.com URL and save it to your
    echo        Render dashboard environment variable: CLOUDFLARE_TUNNEL_URL
    echo.
    cloudflared tunnel --url http://localhost:8000
)

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Cloudflare tunnel exited with error code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
