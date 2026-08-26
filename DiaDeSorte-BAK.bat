@echo off
title DiaDeSorte - Sistema de Analises e Geradores

echo Iniciando servidor...

cd /d "%~dp0"

call .venv\Scripts\activate

start "Servidor Principal" cmd /k "python app.py"

:: Aguarda 5 segundos para o servidor subir completamente
timeout /t 5 >nul

:: Usando o navegador padrao do Windows

:: 1. Visão Geral (Dashboard e Analises Brutas da Loteria)
start "" "http://127.0.0.1:5151/"
timeout /t 2 >nul


:: 3. A Batedeira - Filtrador de Cartelas
start "" "http://127.0.0.1:5151/dashboard-analises"
start "" "http://127.0.0.1:5151/visualizacao-tubular"
start "" "http://127.0.0.1:5151/analise-visual/#pane-simulador-filtros"
start "" "http://127.0.0.1:5151/analise/estrutura-apostas"
start "" "http://127.0.0.1:5151/estatisticas#gerador-palpites"
start "" "http://127.0.0.1:5151/gerador-especial/#independente"
start "" "http://127.0.0.1:5151/analise-ausentes"





exit


