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

        def fix_right_side(match):
            # Transform whatever the class was to position: absolute; right: 15px; top: 50%; transform: translateY(-50%);
            # Assumes it matches <span class="ms-2" ...> or <span class="ms-2">
            full_match = match.group(0)
            if 'position: absolute' in full_match:
                return full_match
            if 'style="' in full_match:
                return full_match.replace('style="', 'style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); ')
            elif "style='" in full_match:
                return full_match.replace("style='", "style='position: absolute; right: 15px; top: 50%; transform: translateY(-50%); ")
            else:
                return full_match.replace('class="ms-2"', 'class="ms-2" style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%);"')

        content, total = re.subn(r'<span[^>]*class=[\'"]ms-2[\'"][^>]*>', fix_right_side, content)
        
        # Specific for Timemania that has color:var(--accent-time) without ms-2 anymore due to previous replace
        content, c_time = re.subn(r'<span style="margin-left:4px;color:var\(--accent-time\);">', 
                                  r'<span style="position: absolute; right: 15px; top: 50%; transform: translateY(-50%); margin-left:4px;color:var(--accent-time);">', content)
        total += c_time

        # Force all .aposta-row to be relative in CSS
        if '.aposta-row {' in content and 'position: relative;' not in content:
            content = content.replace(
                '.aposta-row {\n', 
                '.aposta-row {\n    position: relative;\n'
            )
            content = content.replace(
                '.aposta-row {\r\n', 
                '.aposta-row {\r\n    position: relative;\r\n'
            )

        if total > 0:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Patched thoroughly: {html_path} (replacements: {total})")
