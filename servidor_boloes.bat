@echo off
title Servidor Boloes - DiaDeSorte

echo Iniciando servidor de boloes...

REM Ir para a pasta do projeto
cd /d "%~dp0"

REM Ativar ambiente virtual
call .venv\Scripts\activate

REM Iniciar servidor
python servidor_boloes.py

pause