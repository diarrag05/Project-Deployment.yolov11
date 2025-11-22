@echo off
REM Entraîner le modele
cd /d "c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment n Maintenance\Project-Deployment.yolov11"
echo.
echo Entraînement en cours... Cela prendra environ 2-3 minutes
echo.
C:\Users\mdiia\anaconda3\python.exe fast_train.py
pause
