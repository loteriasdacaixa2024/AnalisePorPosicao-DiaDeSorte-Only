content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

idx_dig = content.find('fat_dig')
idx2 = content.rfind('<div class="row g-1">', 0, idx_dig)
idx3 = content.find('fat_gemeas')
idx4 = content.find('</div>', idx3) + 6
print(f"Section: {idx2} to {idx4}")
print(repr(content[idx2:idx4]))
