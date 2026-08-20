@echo off
setlocal

title MILO - My Intelligent Local Organizer

cd /d "%~dp0"

echo.
echo ==========================================
echo              M.I.L.O
echo      My Intelligent Local Organizer
echo ==========================================
echo.

echo Checking Python...

python --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo Python was not found.
    echo.
    echo Please install Python 3.11 or newer from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python found.
echo.

echo Checking Ollama...

ollama --version >nul 2>&1

if errorlevel 1 (
    echo.
    echo Ollama was not found.
    echo.
    echo Please install Ollama from:
    echo https://ollama.com/download
    echo.
    pause
    exit /b 1
)

echo Ollama found.
echo.

echo Checking Ollama server...

curl -s http://127.0.0.1:11434/api/tags >nul 2>&1

if errorlevel 1 (
    echo Starting Ollama...

    start "" ollama serve

    timeout /t 5 /nobreak >nul
)

echo.
echo Checking qwen3:8b...

ollama list | findstr /C:"qwen3:8b" >nul 2>&1

if errorlevel 1 (
    echo.
    echo qwen3:8b was not found.
    echo MILO will download it now.
    echo This is approximately 5 GB.
    echo.

    ollama pull qwen3:8b

    if errorlevel 1 (
        echo.
        echo Failed to download qwen3:8b.
        echo Please make sure Ollama is running and try again.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo qwen3:8b is ready.
echo.

if not exist ".venv" (
    echo Creating MILO Python environment...

    python -m venv .venv

    if errorlevel 1 (
        echo.
        echo Failed to create Python environment.
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Activating MILO environment...

call ".venv\Scripts\activate.bat"

echo.
echo Installing required packages...

python -m pip install --upgrade pip

pip install -r "Backend\requirements.txt"

if errorlevel 1 (
    echo.
    echo Failed to install Python dependencies.
    echo.
    pause
    exit /b 1
)

echo.
echo Starting MILO backend...
echo.

start "" cmd /k "cd /d ""%~dp0Backend"" && call ""%~dp0.venv\Scripts\activate.bat"" && uvicorn main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo.
echo Opening MILO...
echo.

start "" "https://milo-stardance.vercel.app"

echo.
echo ==========================================
echo MILO is running.
echo.
echo Keep this window open while using MILO.
echo ==========================================
echo.

pause