content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

idx_style_before_script = content.rfind('<style>', 0, 157494)
print("last style before script at:", idx_style_before_script)
print(repr(content[idx_style_before_script-300:idx_style_before_script+30]))
