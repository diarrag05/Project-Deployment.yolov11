@echo off
REM Batch file to run Python scripts with Anaconda
REM Pour Windows: double-cliquez sur ce fichier

REM Vérifier si Python est disponible
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found in PATH
    echo Looking for Anaconda Python...
    
    if exist "C:\Users\mdiia\anaconda3\python.exe" (
        set PYTHON=C:\Users\mdiia\anaconda3\python.exe
    ) else (
        echo Error: Python not found
        echo Please install Anaconda or add Python to PATH
        pause
        exit /b 1
    )
) else (
    set PYTHON=python
)

echo ==============================================================================
echo YOLOv11 SEGMENTATION - LAUNCHER
echo ==============================================================================
echo.
echo Available commands:
echo  1. setup     - Setup and install dependencies
echo  2. test      - Test the project
echo  3. train     - Simple training
echo  4. train-adv - Advanced training
echo  5. evaluate  - Evaluate model
echo  6. infer     - Inference
echo  7. void_rate - Calculate void rate
echo.

set /p CHOICE="Enter choice (1-7) or 'q' to quit: "

if "%CHOICE%"=="q" goto end
if "%CHOICE%"=="1" goto setup
if "%CHOICE%"=="2" goto test
if "%CHOICE%"=="3" goto train
if "%CHOICE%"=="4" goto train_adv
if "%CHOICE%"=="5" goto evaluate
if "%CHOICE%"=="6" goto infer
if "%CHOICE%"=="7" goto void_rate

echo Invalid choice
goto end

:setup
%PYTHON% simple_setup.py
pause
goto end

:test
%PYTHON% test_project.py
pause
goto end

:train
%PYTHON% simple_train.py
pause
goto end

:train_adv
%PYTHON% train.py
pause
goto end

:evaluate
%PYTHON% evaluate.py
pause
goto end

:infer
%PYTHON% inference.py
pause
goto end

:void_rate
%PYTHON% void_rate_calculator.py
pause
goto end

:end
echo.
echo Bye!
