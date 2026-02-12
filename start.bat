@echo off
REM Startup script for Predictive Infrastructure Intelligence System - Windows

setlocal enabledelayedexpansion

echo.
echo 🚀 Predictive Infrastructure Intelligence System - Local Startup
echo =============================================================="
echo.

REM Check Python
echo 📌 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python not found. Please install Python 3.9+
    echo.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% found
echo.

REM Check virtual environment
echo 📌 Checking Python virtual environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo ✓ Virtual environment created
) else (
    echo ✓ Virtual environment exists
)

REM Activate virtual environment
echo 📌 Activating virtual environment...
call venv\Scripts\activate.bat
echo ✓ Virtual environment activated
echo.

REM Install requirements
echo 📌 Installing Python dependencies...
pip install -q -r requirements.txt
echo ✓ Dependencies installed
echo.

REM Display startup summary
echo ════════════════════════════════════════════════════════════
echo ✓ System Ready for Launch
echo ════════════════════════════════════════════════════════════
echo.

echo 📝 Startup Summary:
echo   • Mode: Local Development
echo   • Backend: Flask (http://localhost:5000)
echo   • Frontend: Direct HTML (http://localhost:5000)
echo   • Kubernetes: Demo Mode (simulated metrics)
echo.

echo 🚀 Starting Backend Service...
echo.
echo    ▸ Monitoring Service: Starting...
echo    ▸ ML Engine: Initialized
echo    ▸ API Server: Running on port 5000
echo.
echo 📖 Quick Links:
echo    • Frontend: http://localhost:5000
echo    • Health Check: http://localhost:5000/api/health
echo    • Events: http://localhost:5000/api/events
echo    • Stats: http://localhost:5000/api/stats
echo.
echo To stop the server, press Ctrl+C
echo.
echo.

REM Start the app
python app.py

pause
