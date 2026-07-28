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

:: 5. O Microscópio - Central de Conferências (Onde o Tesouro é Descoberto)

start "" "http://127.0.0.1:5151/central-conferencias" :: combinacoes_filtradas_Jan_20260323_060745.txt
start "" "http://127.0.0.1:5151/analise/conferidor-apostas"
start "" "http://127.0.0.1:5151/monitoramento-apostas/"
start "" "http://127.0.0.1:5151/central-garantias"
start "" "http://127.0.0.1:5151/analise/simulador-apostas"

exit
