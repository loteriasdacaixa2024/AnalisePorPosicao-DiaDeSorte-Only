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

:: 3. A Batedeira - Filtrador de Cartelas

:: Mil vezes melhor este POR FILTRAR  LIXOS
start "" "http://127.0.0.1:5151/filtrador-combinacoes"
start "" "http://127.0.0.1:5151/combinacoes-inteligentes"




exit