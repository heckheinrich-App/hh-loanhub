@echo off
setlocal EnableDelayedExpansion

title HH LOANHUB - Stop Background Services
cd /d "%~dp0\.."

echo ==============================================================================
echo                 HH LOANHUB - SHUTDOWN BACKGROUND SERVICES
echo ==============================================================================
echo.

:: -----------------------------------------------------------------------------
:: 1. Terminate Cloudflare Tunnel process
:: -----------------------------------------------------------------------------
echo [1/3] Terminating Cloudflare Tunnel (cloudflared.exe)...
taskkill /F /IM cloudflared.exe >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   - cloudflared.exe stopped successfully.
) else (
    echo   - cloudflared.exe was not running.
)

:: -----------------------------------------------------------------------------
:: 2. Terminate python process specifically running run_server.py
:: -----------------------------------------------------------------------------
echo [2/3] Terminating Local Engine (run_server.py)...
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -like '*run_server.py*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force; Write-Host ('   - Stopped PID ' + $_.ProcessId + ' (' + $_.Name + ')') }" >nul 2>&1

:: -----------------------------------------------------------------------------
:: 3. Terminate any lingering process listening on port 8000
:: -----------------------------------------------------------------------------
echo [3/3] Checking Port 8000 listeners...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
    set PID_8000=%%a
    if defined PID_8000 (
        echo   - Port 8000 is occupied by PID !PID_8000!. Terminating process...
        taskkill /F /PID !PID_8000! >nul 2>&1
    )
)

echo.
echo ==============================================================================
echo [SUCCESS] All HH LOANHUB background services have been stopped.
echo ==============================================================================
echo.
pause
exit /b 0
