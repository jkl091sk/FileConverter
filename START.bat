@echo off
setlocal
cd /d "%~dp0"
title FileConverter
if not exist ".venv\Scripts\python.exe" (
 echo Run INSTALL.bat first.
 pause & exit /b 1
)
if not exist ".env" copy /Y ".env.example" ".env" >nul
".venv\Scripts\python.exe" -c "from config import config; raise SystemExit(0 if config.bot_token.strip() else 1)"
if errorlevel 1 (
 echo BOT_TOKEN is empty. I will open .env now.
 notepad ".env"
 pause & exit /b 1
)
echo FileConverter is starting. Press Ctrl+C to stop.
".venv\Scripts\python.exe" bot.py
if errorlevel 1 pause
