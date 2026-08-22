@echo off
setlocal EnableExtensions

title MILO - My Intelligent Local Organizer

cd /d "%~dp0"

echo.
echo ==========================================
echo              M.I.L.O
echo       My Intelligent Local Organizer
echo ==========================================
echo.

echo [1/7] Checking Python...

python --version >nul 2>&1

if %errorlevel% neq 0 (
    echo Python is not installed correctly.
    echo Installing Python 3.11...
    echo.

    winget install --id Python.Python.3.11 -e --accept-source-agreements --accept-package-agreements

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not install Python automatically.
        echo Please install Python 3.11 or newer and run MILO again.
        pause
        exit /b 1
    )

    echo.
    echo Python was installed.
    echo Please close this window and run Start MILO.bat again.
    pause
    exit /b 0
)

for /f "tokens=2" %%A in ('python --version 2^>^&1') do set PYTHON_VERSION=%%A

echo Python %PYTHON_VERSION% found.

echo.
echo [2/7] Checking Ollama...

ollama --version >nul 2>&1

if %errorlevel% neq 0 (
    echo Ollama is not installed correctly.
    echo Installing Ollama...
    echo.

    winget install --id Ollama.Ollama -e --accept-source-agreements --accept-package-agreements

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not install Ollama automatically.
        echo Please install Ollama and run MILO again.
        pause
        exit /b 1
    )

    echo.
    echo Ollama was installed.
    echo Please close this window and run Start MILO.bat again.
    pause
    exit /b 0
)

echo Ollama found.

echo.
echo [3/7] Checking Tesseract OCR...

where tesseract >nul 2>&1

if %errorlevel% neq 0 (

    if exist "%ProgramFiles%\Tesseract-OCR\tesseract.exe" (
        set "PATH=%PATH%;%ProgramFiles%\Tesseract-OCR"
    )

    if exist "%ProgramFiles(x86)%\Tesseract-OCR\tesseract.exe" (
        set "PATH=%PATH%;%ProgramFiles(x86)%\Tesseract-OCR"
    )
)

where tesseract >nul 2>&1

if %errorlevel% neq 0 (
    echo Tesseract OCR is not installed.
    echo Installing Tesseract OCR...
    echo.

    winget install --id tesseract-ocr.tesseract -e --accept-source-agreements --accept-package-agreements

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Could not install Tesseract OCR automatically.
        echo.
        echo MILO can still work with normal text PDFs,
        echo but scanned PDFs and images will not have OCR.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo Tesseract OCR was installed.
    echo Please close this window and run Start MILO.bat again.
    pause
    exit /b 0
)

echo Tesseract OCR found.

echo.
echo [4/7] Checking Python dependencies...

python -c "import fastapi, uvicorn, pydantic, ollama, pypdf, pymupdf" >nul 2>&1

if %errorlevel% neq 0 (
    echo MILO dependencies are missing.
    echo Installing dependencies...
    echo.

    python -m pip install -r Backend\requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: Failed to install MILO dependencies.
        echo.
        pause
        exit /b 1
    )
)

echo Dependencies ready.

echo.
echo [5/7] Checking AI model...

ollama list | findstr /C:"qwen3:8b" >nul 2>&1

if %errorlevel% neq 0 (
    echo qwen3:8b is not installed.
    echo Downloading the MILO AI model...
    echo This may take a while.
    echo.

    ollama pull qwen3:8b

    echo.
    echo Verifying AI model...

    ollama list | findstr /C:"qwen3:8b" >nul 2>&1

    if %errorlevel% neq 0 (
        echo.
        echo ERROR: qwen3:8b was not detected after downloading.
        echo.
        echo Run this command manually to check:
        echo ollama list
        echo.
        pause
        exit /b 1
    )

    echo AI model downloaded successfully.
)

echo AI model ready.

echo.
echo [6/7] Starting MILO backend...

start "MILO Backend" cmd /k "cd /d "%~dp0Backend" && python -m uvicorn main:app --reload"

timeout /t 3 /nobreak >nul

echo.
echo [7/7] Opening MILO...

start "" "%~dp0Frontend\index.html"

echo.
echo ==========================================
echo           MILO IS RUNNING
echo ==========================================
echo.
echo Backend: http://127.0.0.1:8000
echo.
echo OCR: Tesseract
echo AI: qwen3:8b
echo.
echo Keep the MILO Backend window open.
echo.

pause