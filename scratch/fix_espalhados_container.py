content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

old = '<div id="placard_espalhados" class="d-flex flex-row flex-wrap justify-content-center gap-2">'
new = '<div id="placard_espalhados" class="d-flex flex-row gap-2 w-100">'

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    idx = content.find('placard_espalhados" class=')
    print("NOT FOUND, current:", repr(content[idx:idx+120]) if idx>0 else "element not found")
