@echo off
title MILO

cd /d "%~dp0Backend"

echo.
echo ==============================
echo          M.I.L.O
echo ==============================
echo.

echo Checking Python...

python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed.
    echo Please install Python 3.11 or newer.
    echo.
    pause
    exit /b
)

echo Python found.
echo.

echo Installing required Python packages...
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Could not install the required packages.
    echo.
    pause
    exit /b
)

echo.
echo Starting MILO backend...
echo.

python -m uvicorn main:app --host 127.0.0.1 --port 8000

pause