@echo off
title DiaDeSorte - Sistema de Analises e Geradores

echo Iniciando servidor...

cd /d "%~dp0"

call .venv\Scripts\activate

start "Servidor Principal" cmd /k "python app.py"

:: Aguarda 5 segundos para o servidor subir completamente
timeout /t 5 >nul

:: Usando o navegador padrao do Windows

::Visão Geral (Dashboard e Analises Brutas da Loteria)
start "" "http://127.0.0.1:5151/"
timeout /t 2 >nul

:: 1. Visão Geral (Dashboard e Analises Brutas da Loteria)

start "" "http://127.0.0.1:5151/indice-analises"
start "" "http://127.0.0.1:5151/dashboard-analises"
start "" "http://127.0.0.1:5151/dashboard-analises-v2"
start "" "http://127.0.0.1:5151/estatisticas"
start "" "http://127.0.0.1:5151/analise-visual/"
start "" "http://127.0.0.1:5151/analise-profunda"
start "" "http://127.0.0.1:5151/analise-ausentes"
start "" "http://127.0.0.1:5151/analise-ciclos-dezenas"
start "" "http://127.0.0.1:5151/posicao-minima-maxima"
start "" "http://127.0.0.1:5151/cruzamentos/dashboard"



exit
