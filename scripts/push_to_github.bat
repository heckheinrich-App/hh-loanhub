@echo off
setlocal EnableDelayedExpansion

title HH LOANHUB - Push to GitHub
cd /d "%~dp0\.."

echo ==============================================================================
echo                 HH LOANHUB - GIT CI/CD PUBLISH PIPELINE
echo ==============================================================================
echo Project Root: %CD%
echo.

:: Verify git is installed and repository exists
where git >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Git is not installed or not found in system PATH.
    echo Please install Git for Windows from https://git-scm.com/
    pause
    exit /b 1
)

if not exist ".git" (
    echo [WARNING] No Git repository detected in this directory.
    echo Initializing Git repository now...
    git init
    git branch -M main
    echo Repository initialized. Make sure you set your remote:
    echo   git remote add origin https://github.com/YOUR_USERNAME/hh-loanhub.git
    echo.
)

:: Show current repository status
echo Current Git Status:
echo ------------------------------------------------------------------------------
git status -s
echo ------------------------------------------------------------------------------
echo.

:: Generate default timestamp
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd HH:mm:ss'"`) do set TIMESTAMP=%%I
if "!TIMESTAMP!"=="" (
    set TIMESTAMP=%DATE% %TIME%
)

:: Prompt for commit message
set /p COMMIT_MSG="Enter commit message (Press ENTER for default '%TIMESTAMP%'): "
if "!COMMIT_MSG!"=="" (
    set COMMIT_MSG=HH LOANHUB update - !TIMESTAMP!
)

echo.
echo [1/3] Staging all tracked and new files...
git add .
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to stage files.
    pause
    exit /b %ERRORLEVEL%
)

echo [2/3] Committing changes with message: "!COMMIT_MSG!"...
git commit -m "!COMMIT_MSG!"
if %ERRORLEVEL% neq 0 (
    echo [NOTE] Nothing new to commit, or commit encountered an issue.
)

echo [3/3] Pushing to GitHub (origin/main)...
git push origin main
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Push to remote branch 'main' failed.
    echo Suggestions:
    echo   - Check if remote is configured: git remote -v
    echo   - If this is your first push: git push -u origin main
    echo   - Verify your GitHub credentials and network access.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo [SUCCESS] Code pushed successfully to GitHub!
echo Render will automatically trigger deployment of the Gateway.
echo ==============================================================================
pause
exit /b 0
