@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title FileConverter - Install
echo === FileConverter Windows Installer ===
where py >nul 2>nul
if not errorlevel 1 (set "PY=py -3") else (set "PY=python")
%PY% -c "import sys; print('Python',sys.version.split()[0]); raise SystemExit(0 if sys.version_info >= (3,12) else 1)"
if errorlevel 1 (
 echo Python 3.12+ is required. Install it from python.org and enable Add Python to PATH.
 pause & exit /b 1
)
if not exist ".venv\Scripts\python.exe" %PY% -m venv .venv
if errorlevel 1 goto fail
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto fail
where ffmpeg >nul 2>nul
if errorlevel 1 (
 echo FFmpeg not found. Trying winget...
 where winget >nul 2>nul && winget install --id Gyan.FFmpeg -e --accept-package-agreements --accept-source-agreements
)
set "LO=0"
where soffice >nul 2>nul && set "LO=1"
if exist "%ProgramFiles%\LibreOffice\program\soffice.exe" set "LO=1"
if "%LO%"=="0" (
 echo LibreOffice not found. Trying winget...
 where winget >nul 2>nul && winget install --id TheDocumentFoundation.LibreOffice -e --accept-package-agreements --accept-source-agreements
)
if not exist data mkdir data
if not exist temp mkdir temp
".venv\Scripts\python.exe" -c "import asyncio; from database.database import init_db; asyncio.run(init_db())"
if errorlevel 1 goto fail
if not exist ".env" copy /Y ".env.example" ".env" >nul
echo.
echo Installation complete.
echo Open .env, paste BOT_TOKEN, save it, then double-click START.bat.
pause
exit /b 0
:fail
echo Installation failed. Check the error above.
pause
exit /b 1
