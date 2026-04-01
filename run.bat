@echo off
REM WaveSync Quick Start Script for Windows

echo.
echo 🚀 WaveSync - Cloud Migration Control Center
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo ✅ Python found: 
python --version

REM Check if venv exists, if not create it
if not exist "venv\" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

echo.
echo ========================================
echo 🎯 WaveSync is ready!
echo ========================================
echo.
echo To start the API server:
echo   python src/wavesync/frontend/app.py
echo.
echo To start the Streamlit dashboard:
echo   streamlit run frontend/dashboard.py
echo.
echo ========================================
echo.
