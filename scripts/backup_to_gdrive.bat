@echo off
setlocal EnableDelayedExpansion

title HH LOANHUB - Local Database Backup to Google Drive
cd /d "%~dp0\.."

echo ==============================================================================
echo                 HH LOANHUB - GOOGLE DRIVE ZERO-LOSS BACKUP
echo ==============================================================================
echo Project Root: %CD%

set DATA_DIR=%CD%\data
set TARGET_GDRIVE=

:: Check user profile Google Drive first
if exist "C:\Users\%USERNAME%\Google Drive" (
    set TARGET_GDRIVE=C:\Users\%USERNAME%\Google Drive\HH_LOANHUB_Backups
)

:: Attempt to parse GDRIVE_BACKUP_PATH from .env if present
if exist ".env" (
    for /f "usebackq tokens=1,* delims==" %%A in (".env") do (
        set KEY=%%A
        set VAL=%%B
        if /i "!KEY!"=="GDRIVE_BACKUP_PATH" (
            if not "!VAL!"=="" set TARGET_GDRIVE=!VAL!
        )
    )
)

if "!TARGET_GDRIVE!"=="" (
    set TARGET_GDRIVE=C:\Users\Public\GoogleDrive\HH_LOANHUB_Backups
)

:: Trim possible trailing quotes or spaces
set TARGET_GDRIVE=!TARGET_GDRIVE:"=!

echo Local Data Path: %DATA_DIR%
echo Target Backup:   %TARGET_GDRIVE%
echo.

if not exist "%DATA_DIR%" (
    echo [ERROR] Local data directory '%DATA_DIR%' does not exist.
    pause
    exit /b 1
)

:: Generate timestamp for backup folder: YYYY-MM-DD_HH-MM-SS
for /f "usebackq tokens=*" %%I in (`powershell -NoProfile -Command "Get-Date -Format 'yyyy-MM-dd_HH-mm-ss'"`) do set TS=%%I
if "!TS!"=="" (
    set TS=%DATE:~-4%-%DATE:~4,2%-%DATE:~7,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%
    set TS=!TS:/=-!
    set TS=!TS: =0!
)

set BACKUP_SUBDIR=%TARGET_GDRIVE%\backup_!TS!
set LATEST_SYNC=%TARGET_GDRIVE%\latest

echo Creating timestamped snapshot: !BACKUP_SUBDIR!
if not exist "!BACKUP_SUBDIR!" mkdir "!BACKUP_SUBDIR!"
if not exist "!LATEST_SYNC!" mkdir "!LATEST_SYNC!"

:: Use Robocopy to copy all contents of data folder (excluding gitkeep if preferred, or keeping all)
echo [1/2] Copying data folder to timestamped snapshot...
robocopy "%DATA_DIR%" "!BACKUP_SUBDIR!" /E /R:2 /W:2 /NP /NFL /NDL
set ROBO_ERR=%ERRORLEVEL%
:: Robocopy return codes 0-7 mean success/files copied
if %ROBO_ERR% geq 8 (
    echo [ERROR] Robocopy snapshot failed with exit code %ROBO_ERR%.
    pause
    exit /b %ROBO_ERR%
)

echo [2/2] Mirroring to latest snapshot sync folder...
robocopy "%DATA_DIR%" "!LATEST_SYNC!" /MIR /R:2 /W:2 /NP /NFL /NDL

:: Create a backup manifest
(
    echo Backup Timestamp: !TS!
    echo Source Directory: %DATA_DIR%
    echo Target Directory: !BACKUP_SUBDIR!
    echo Computer Name: %COMPUTERNAME%
    echo Username: %USERNAME%
) > "!BACKUP_SUBDIR!\backup_manifest.txt"

echo.
echo ==============================================================================
echo [SUCCESS] Backup completed successfully!
echo Snapshot created at: !BACKUP_SUBDIR!
echo Google Drive desktop client will automatically sync this to cloud storage.
echo ==============================================================================
echo.
pause
exit /b 0
