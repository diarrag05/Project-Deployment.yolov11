@echo off
REM YOLOv11 Segmentation Platform - Windows Startup Script
REM Phase 2: Flask Web Application

cls
color 0A
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                                                                  ║
echo ║   YOLOv11 Segmentation Platform - Phase 2 Launcher             ║
echo ║                                                                  ║
echo ║   Backend: Flask REST API                                       ║
echo ║   Frontend: HTML5 + CSS3 + JavaScript                          ║
echo ║   ML Models: YOLOv8n-seg + SAM                                 ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo [✓] Python found
python --version

REM Check if requirements are installed
echo.
echo Checking dependencies...
pip show flask >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [!] Installing required packages...
    echo This may take a few minutes...
    echo.
    pip install -r requirements_api.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo [✓] All dependencies are installed
)

REM Check if YOLO model exists
if not exist "yolov8n-seg.pt" (
    echo.
    echo [!] YOLOv8n-seg model not found
    echo Downloading model... (This may take a minute)
    python -c "from ultralytics import YOLO; YOLO('yolov8n-seg.pt')"
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to download model
        pause
        exit /b 1
    )
)
echo [✓] Model file verified

REM Create necessary directories
echo.
echo Creating directories...
if not exist "labeled_data" mkdir labeled_data
if not exist "labeled_data\labels" mkdir labeled_data\labels
if not exist "models" mkdir models
if not exist "reports" mkdir reports
if not exist "uploads" mkdir uploads
echo [✓] Directories ready

REM Start the Flask application
echo.
echo ╔══════════════════════════════════════════════════════════════════╗
echo ║                 Starting Flask Application...                   ║
echo ║                                                                  ║
echo ║   Home Page:       http://localhost:5000/                       ║
echo ║   Analysis:        http://localhost:5000/analysis               ║
echo ║   Dashboard:       http://localhost:5000/dashboard              ║
echo ║   API Health:      http://localhost:5000/api/health             ║
echo ║                                                                  ║
echo ║   To stop: Press CTRL+C                                         ║
echo ║                                                                  ║
echo ╚══════════════════════════════════════════════════════════════════╝
echo.

REM Run Flask
python app.py

REM If Flask stops, show error
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Flask application failed to start
    echo Check the error messages above for details
    pause
    exit /b 1
)

pause
