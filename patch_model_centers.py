import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')
base_dir = 'd:/LoteriasPosicao'

for folder in os.listdir(base_dir):
    if not os.path.isdir(os.path.join(base_dir, folder)): continue
    if not folder.startswith('AnalisePorPosicao'): continue
        
    html_path = os.path.join(base_dir, folder, 'templates', 'modelos.html')
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Substituir '<div id="card-{{ m.id }}" class="col-12 mb-4"' por col-12 col-xl-8 col-lg-10 mx-auto mb-4
        content, count = re.subn(r'class=[\'"]col-12 mb-4[\'"]', 'class="col-12 col-xl-8 col-lg-10 mx-auto mb-4"', content)
        
        # Centralizar a div com os botoes dos tab (nav-buttons)
        content, count_btn = re.subn(r'class=[\'"]d-flex flex-wrap gap-2 mb-4[\'"]', 'class="d-flex flex-wrap gap-2 justify-content-center mx-auto mb-4" style="max-width: 800px;"', content)

        if count > 0 or count_btn > 0:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched successfully: {html_path} (cards={count}, btns={count_btn})")
        else:
            print(f"No match in {html_path}")
