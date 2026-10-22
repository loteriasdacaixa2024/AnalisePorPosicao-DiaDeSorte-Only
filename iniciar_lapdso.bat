@echo off
cd /d "%~dp0"
set "PYTHON=%~dp0LAPDSO_venv\Scripts\python.exe"
set "URL=http://127.0.0.1:5151/"
if not exist "%PYTHON%" set "PYTHON=python"
powershell -NoProfile -Command "try { $c = New-Object Net.Sockets.TcpClient; $c.Connect('127.0.0.1',5151); $c.Close(); exit 0 } catch { exit 1 }"
if errorlevel 1 (
  start "LAPDSO" /MIN "%PYTHON%" "%~dp0LAPDSO.py"
  timeout /t 8 /nobreak >nul
)
start "" "%URL%"
