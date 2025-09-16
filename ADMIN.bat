@echo off
:: Vérifie si on est admin
NET SESSION >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Elevation required. Relaunching as admin...
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

:: Se placer dans le dossier du script (BETA-MULTITOOL)
cd /d "%~dp0"

:: Lancer le script Python sans console
start "" pythonw.exe main.py
