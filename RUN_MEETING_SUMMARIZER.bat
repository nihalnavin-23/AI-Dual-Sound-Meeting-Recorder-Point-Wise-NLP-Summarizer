@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

title OmniMeet - AI Meeting Recorder & Point-Wise NLP Summarizer
color 0B
cls

echo =====================================================================
echo    OMNIMEET : DUAL-SOUND MEETING RECORDER & POINT-WISE NLP SUMMARIZER
echo         Captures Mic + Zoom/Teams/Meet Audio -> Point-Wise MoM
echo =====================================================================
echo.
echo [*] Working Directory: %CD%

:: Locate Working Python Executable
set "PYTHON_BIN="

python --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_BIN=python"
    goto :python_found
)

py --version >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_BIN=py"
    goto :python_found
)

if exist "C:\Program Files\Python312\python.exe" (
    set "PYTHON_BIN=C:\Program Files\Python312\python.exe"
    goto :python_found
)

if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    set "PYTHON_BIN=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    goto :python_found
)

:python_found
if not defined PYTHON_BIN (
    echo [ERROR] Python was not found on your system PATH.
    echo Please install Python 3.10+ and check 'Add Python to PATH'.
    echo.
    pause
    exit /b 1
)

echo [*] Python Interpreter: %PYTHON_BIN%
"%PYTHON_BIN%" --version

:: Verify Python Packages
echo.
echo [*] Checking core libraries: streamlit, reportlab...
"%PYTHON_BIN%" -c "import streamlit, reportlab" >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Installing required libraries...
    "%PYTHON_BIN%" -m pip install streamlit reportlab SpeechRecognition numpy
) else (
    echo [OK] Core libraries verified.
)

echo.
echo =====================================================================
echo [*] Starting Streamlit Meeting Cockpit on http://localhost:8501...
echo [*] Your default browser will open automatically...
echo =====================================================================
echo.

"%PYTHON_BIN%" -m streamlit run app.py --server.headless false

pause
