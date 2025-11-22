@echo off
REM Lancer TensorBoard automatiquement
REM Double-clique sur ce fichier pour démarrer TensorBoard

cd /d "c:\Users\mdiia\OneDrive\Bureau\AIVANCITY\Cours\PGE4\Deployment n Maintenance\Project-Deployment.yolov11"

echo.
echo ==============================================================================
echo   TensorBoard - Démarrage en cours...
echo ==============================================================================
echo.
echo   Ouvre http://localhost:6006/ dans ton navigateur
echo   Appuie sur Ctrl+C pour arrêter
echo.
echo ==============================================================================
echo.

C:\Users\mdiia\anaconda3\python.exe -m tensorboard.main --logdir "runs\segment\train2" --port 6006

pause
