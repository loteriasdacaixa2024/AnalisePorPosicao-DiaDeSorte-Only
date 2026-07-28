@echo off
title Iniciar Servidores Boloes
echo Abrindo os terminais de servidores...

set "RAIZ=D:\Loterias\AnalisePorPosicao-DiaDeSorte-Only"
set "PY=%RAIZ%\.venv\Scripts\python.exe"
set "WT=%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe"

if not exist "%PY%" (
    echo.
    echo ERRO: Python do venv nao encontrado:
    echo   %PY%
    echo.
    pause
    exit /b 1
)

set PYTHONUNBUFFERED=1

if exist "%WT%" (
    "%WT%" -d "%RAIZ%" cmd /k "cd /d \"%RAIZ%\" && title Servidor 5151 && echo ======================================== && echo   SERVIDOR PRINCIPAL - app.py && echo   http://localhost:5151 && echo ======================================== && echo Pressione uma tecla para ligar... && pause && \"%PY%\" app.py" ; split-pane -H -d "%RAIZ%" cmd /k "cd /d \"%RAIZ%\" && title Extrator Boloes Caixa && echo ======================================== && echo   EXTRATOR DE BOLOES - Caixa API && echo ======================================== && echo [1] login + modalidade + filtros + ENTER && echo Pressione uma tecla para abrir o menu... && pause && \"%PY%\" -u conferencias-boloes\script\baixar_boloes-API.py"
) else (
    echo Windows Terminal nao encontrado — abrindo duas janelas CMD...
    start "Servidor 5151" cmd /k "cd /d \"%RAIZ%\" && title Servidor 5151 && echo http://localhost:5151 && pause && \"%PY%\" app.py"
    start "Extrator Boloes Caixa" cmd /k "cd /d \"%RAIZ%\" && title Extrator Boloes && pause && \"%PY%\" -u conferencias-boloes\script\baixar_boloes-API.py"
)
