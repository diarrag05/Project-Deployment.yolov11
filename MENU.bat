@echo off
REM Quick commands - Double-clique sur le fichier que tu veux

setlocal enabledelayedexpansion

:menu
cls
echo.
echo ==============================================================================
echo   COMMANDES RAPIDES - Projet YOLOv8 Segmentation
echo ==============================================================================
echo.
echo   1. Verifier le projet (CHECK.py)
echo   2. Guide interactif (GET_STARTED.py)
echo   3. Entraîner le modèle (fast_train.py)
echo   4. Faire une inference (inference.py)
echo   5. Calculer taux de vides (void_rate_calculator.py)
echo   6. Evaluer le modele (evaluate.py)
echo   7. Pipeline complet (pipeline.py)
echo   8. Verifier tous les etapes (verify_all_steps.py)
echo   9. Lancer TensorBoard
echo   0. Quitter
echo.
echo ==============================================================================
echo.

set /p choice="Choisis une option (0-9): "

if "%choice%"=="1" goto check
if "%choice%"=="2" goto started
if "%choice%"=="3" goto train
if "%choice%"=="4" goto inference
if "%choice%"=="5" goto voidrate
if "%choice%"=="6" goto evaluate
if "%choice%"=="7" goto pipeline
if "%choice%"=="8" goto verify
if "%choice%"=="9" goto tensorboard
if "%choice%"=="0" goto end
goto menu

:check
echo.
echo Execution de CHECK.py...
C:\Users\mdiia\anaconda3\python.exe CHECK.py
pause
goto menu

:started
echo.
echo Execution de GET_STARTED.py...
C:\Users\mdiia\anaconda3\python.exe GET_STARTED.py
pause
goto menu

:train
echo.
echo Execution de fast_train.py...
echo Cela peut prendre 2-3 minutes...
echo.
C:\Users\mdiia\anaconda3\python.exe fast_train.py
pause
goto menu

:inference
echo.
echo Execution de inference.py...
C:\Users\mdiia\anaconda3\python.exe inference.py
pause
goto menu

:voidrate
echo.
echo Execution de void_rate_calculator.py...
C:\Users\mdiia\anaconda3\python.exe void_rate_calculator.py
pause
goto menu

:evaluate
echo.
echo Execution de evaluate.py...
C:\Users\mdiia\anaconda3\python.exe evaluate.py
pause
goto menu

:pipeline
echo.
echo Execution de pipeline.py...
echo Cela peut prendre 5-10 minutes...
echo.
C:\Users\mdiia\anaconda3\python.exe pipeline.py
pause
goto menu

:verify
echo.
echo Execution de verify_all_steps.py...
C:\Users\mdiia\anaconda3\python.exe verify_all_steps.py
pause
goto menu

:tensorboard
echo.
echo Lancement de TensorBoard...
echo Ouvre http://localhost:6006/ dans ton navigateur
echo Appuie sur Ctrl+C pour arrêter
echo.
C:\Users\mdiia\anaconda3\python.exe -m tensorboard.main --logdir "runs\segment\train2" --port 6006
pause
goto menu

:end
echo.
echo Au revoir!
echo.
exit /b 0
