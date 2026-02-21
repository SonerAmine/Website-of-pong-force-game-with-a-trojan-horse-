@echo off
REM ================================================
REM PONG FORCE - MULTIPLAYER LAUNCHER
REM ================================================

echo.
echo ================================================
echo    PONG FORCE - MULTIPLAYER LAUNCHER
echo ================================================
echo.
echo Ce script facilite le lancement du multiplayer.
echo.
echo Que voulez-vous faire?
echo.
echo [1] Demarrer le serveur matchmaking
echo [2] Jouer (lancer le jeu)
echo [3] Tester le systeme (test_gameplay.py)
echo [4] Installer les dependances
echo [5] Quitter
echo.

set /p choice="Votre choix (1-5): "

if "%choice%"=="1" goto start_matchmaking
if "%choice%"=="2" goto start_game
if "%choice%"=="3" goto run_tests
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto end

echo.
echo Choix invalide!
pause
goto end

:start_matchmaking
echo.
echo ================================================
echo DEMARRAGE DU SERVEUR MATCHMAKING
echo ================================================
echo.
echo Le serveur matchmaking va demarrer...
echo Laissez cette fenetre ouverte pendant que vous jouez!
echo.
echo Pour arreter: Fermez cette fenetre ou appuyez sur Ctrl+C
echo.
pause
python matchmaking_server.py
goto end

:start_game
echo.
echo ================================================
echo LANCEMENT DU JEU
echo ================================================
echo.
echo IMPORTANT: Le serveur matchmaking doit etre en ligne!
echo Si ce n'est pas le cas, ouvrez un autre terminal et
echo executez: python matchmaking_server.py
echo.
pause
python main.py
goto end

:run_tests
echo.
echo ================================================
echo TESTS DU SYSTEME
echo ================================================
echo.
python test_gameplay.py
pause
goto end

:install_deps
echo.
echo ================================================
echo INSTALLATION DES DEPENDANCES
echo ================================================
echo.
echo Installation de pygame, Flask, requests...
echo.
pip install -r requirements.txt
echo.
echo ================================================
echo Installation terminee!
echo ================================================
pause
goto end

:end
echo.
echo A bientot!
exit
