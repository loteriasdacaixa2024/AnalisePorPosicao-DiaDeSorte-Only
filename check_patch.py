import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
html_path = 'd:/LoteriasPosicao/AnalisePorPosicao-DuplaSena-Only/templates/modelos.html'
if os.path.exists(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for x in range(1, 150):
        if '.aposta-num' in lines[x] or 'text-align' in lines[x] or 'width' in lines[x]:
             print(f"{x}: {lines[x].strip()}")
