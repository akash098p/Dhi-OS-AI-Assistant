@echo off
title DHI OS v3.0 - JARVIS Protocol
cd /d "%~dp0"

rem ---------------------------------------------------------------------
rem  Dhi - instant launcher. Double-click this file to talk to her.
rem
rem  NOTE: we always call "python.exe -m streamlit" and NEVER the venv's
rem  streamlit.exe / pip.exe launchers. Those .exe files embed absolute
rem  paths and break with "Fatal error in launcher" when the project
rem  folder is moved or copied to another location/PC.
rem ---------------------------------------------------------------------

set PORT=8501
set "PY_CMD="

rem --- 1) Prefer the project's virtual environment ----------------------
if exist "venv\Scripts\python.exe" (
    "venv\Scripts\python.exe" --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=venv\Scripts\python.exe"
)

rem --- 2) Fall back to any working global Python ------------------------
if not defined PY_CMD (
    python --version >nul 2>&1
    if not errorlevel 1 set "PY_CMD=python"
)

if not defined PY_CMD (
    echo.
    echo   [Dhi] No working Python found on this PC.
    echo         Install Python 3.10 or newer from python.org,
    echo         then run Dhi.bat again.
    echo.
    pause
    exit /b 1
)

rem --- 3) Make sure streamlit is importable (one-time auto-install) -----
"%PY_CMD%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo   [Dhi] Setting up dependencies - one-time step, please wait...
    echo.
    "%PY_CMD%" -m pip install -r requirements.txt
)

echo.
echo   ==============================================
echo      DHI OS v3.0  -  JARVIS Protocol
echo      Your AI Voice Assistant
echo      URL : http://localhost:%PORT%
echo      Your browser will open automatically.
echo      Keep this window open while using Dhi.
echo   ==============================================
echo.

"%PY_CMD%" -m streamlit run app.py --server.port %PORT%

echo.
echo   Dhi has stopped. Press any key to close this window.
pause >nul
