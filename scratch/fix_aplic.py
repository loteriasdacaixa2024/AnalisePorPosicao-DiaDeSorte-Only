content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

old = "let inputId = k === 'gemeas' ? 'fat_gemeas' : `fat_dig_${k}`;"
new = "let inputId = `fat_dig_${k}`;"

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - aplicarLimitesPelaAnalise fixed")
else:
    print("NOT FOUND")
