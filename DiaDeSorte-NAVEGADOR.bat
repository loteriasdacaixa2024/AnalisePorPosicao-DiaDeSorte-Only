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
start "" "http://127.0.0.1:5151/dashboard-analises"
start "" "http://127.0.0.1:5151/visualizacao-tubular"
start "" "http://127.0.0.1:5151/analise-visual/#pane-simulador-filtros"
start "" "http://127.0.0.1:5151/analise/estrutura-apostas"
start "" "http://127.0.0.1:5151/estatisticas#gerador-palpites"
start "" "http://127.0.0.1:5151/gerador-especial/#independente"
start "" "http://127.0.0.1:5151/analise-ausentes"


:: 2. A Fonte - Geradores (Criações Inteligentes, Táticas e Extremas)
::start "" "http://127.0.0.1:5151/gerador-inteligente" :: Neste caso nem preciso usar este 
::start "" "http://127.0.0.1:5151/gerador-padroes"
::start "" "http://127.0.0.1:5151/gerador-especial"
::start "" "http://127.0.0.1:5151/desdobramentos"
::start "" "http://127.0.0.1:5151/desdobramentos#btn-modo-e-manual"
:: 3. A Batedeira - Filtrador de Cartelas
::start "" "http://127.0.0.1:5151/filtrador-combinacoes" :: Mil vezes melhor este POR FILTRAR  LIXOS
:: 4. O Microscópio - Central de Conferências (Onde o Tesouro é Descoberto)
::start "" "http://127.0.0.1:5151/central-conferencias" :: combinacoes_filtradas_Jan_20260323_060745.txt
::start "" "http://127.0.0.1:5151/central-conferencias#conferencia-historica"
::start "" "http://127.0.0.1:5151/central-conferencias#tab-conferencia-boloes"
::start "" "http://127.0.0.1:5151/central-conferencias/resumo-apostas"
::start "" "http://127.0.0.1:5151/monitoramento-apostas/"

exit


