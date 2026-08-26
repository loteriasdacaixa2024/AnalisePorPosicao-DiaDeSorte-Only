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

:: 2. A Fonte - Geradores (Criações Inteligentes, Táticas e Extremas)

start "" "http://127.0.0.1:5151/gerador-especial"
start "" "http://127.0.0.1:5151/gerador-inteligente"
start "" "http://127.0.0.1:5151/gerador-padroes"
start "" "http://127.0.0.1:5151/desdobramentos"
start "" "http://127.0.0.1:5151/ferramentas/fechamentos"
start "" "http://127.0.0.1:5151/analise-ciclos-dezenas/gerador"
start "" "http://127.0.0.1:5151/palpites"
start "" "http://127.0.0.1:5151/desdobramentos"
start "" "http://127.0.0.1:5151/desdobramentos#btn-modo-e-manual"
::QUANDO QUISER DEZENAS INICIADOS COM 1 OU ACIMA DO DIGITO  0 (CICLO POSICIONAL)
start "" "http://127.0.0.1:5151/gerador-especial/#independente"
start "" "http://127.0.0.1:5151/estatisticas#gerador-palpites"
start "" "http://127.0.0.1:5151/visualizacao-tubular"
start "" "http://127.0.0.1:5151/analise/estrutura-apostas"
start "" "http://127.0.0.1:5151/analise-visual/#pane-simulador-filtros"









exit
