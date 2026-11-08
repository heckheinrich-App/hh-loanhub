@echo off
setlocal EnableDelayedExpansion

title HH LOANHUB - Local Core Engine
cd /d "%~dp0\.."

echo ==============================================================================
echo                 HH LOANHUB - LOCAL CORE ENGINE LAUNCHER
echo ==============================================================================
echo Working Directory: %CD%

:: Check for virtual environment in standard folders
if exist "venv\Scripts\python.exe" (
    echo [INFO] Launching FastAPI Core Engine using venv on http://localhost:8000...
    "venv\Scripts\python.exe" run_server.py
    exit /b %ERRORLEVEL%
) else if exist ".venv\Scripts\python.exe" (
    echo [INFO] Launching FastAPI Core Engine using .venv on http://localhost:8000...
    ".venv\Scripts\python.exe" run_server.py
    exit /b %ERRORLEVEL%
)

:: Verify python is available (check PATH and standard user installation)
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PATH=%LOCALAPPDATA%\Programs\Python\Python312;%LOCALAPPDATA%\Programs\Python\Python312\Scripts;!PATH!"
    )
)

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in PATH or the activated virtual environment.
    echo Please install Python 3.10+ and ensure it is added to your system PATH.
    pause
    exit /b 1
)

:: Ensure dependencies are present (optional check)
if not exist "run_server.py" (
    echo [ERROR] run_server.py not found in %CD%!
    pause
    exit /b 1
)

echo [INFO] Launching FastAPI Core Engine on http://localhost:8000...
python run_server.py

if %ERRORLEVEL% neq 0 (
    echo [ERROR] Server terminated unexpectedly with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

exit /b 0
