@echo off
TITLE TIA Portal AutoGen
CLS

ECHO ========================================================
ECHO    Start TIA Portal V20 AutoGen App
ECHO ========================================================
ECHO.

CD /D "%~dp0"

ECHO [1/3] Checking for updates...
pip install -r requirements.txt
IF %ERRORLEVEL% NEQ 0 (
    ECHO Error installing dependencies.
    PAUSE
    EXIT /B
)

ECHO.
ECHO [2/3] Starting Application...
start "" "http://localhost:5000"

ECHO [3/3] Server Running...
python app.py

PAUSE
