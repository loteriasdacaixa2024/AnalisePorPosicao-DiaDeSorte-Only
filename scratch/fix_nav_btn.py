content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

old = """        <button id="btn-aba-analisador" class="btn btn-outline-purple px-4 py-2"
            style="font-weight: bold; font-size: 16px; border-color: #6f42c1; color: #6f42c1;" onclick="mostrarAba('analisador')">
            <i class="fas fa-microscope"></i> 10. Analisador em Massa
        </button>"""

new = """        <button id="btn-aba-analisador" class="btn px-4 py-2"
            style="font-weight: bold; font-size: 16px; border: 2px solid #D4B31A; color: #b69816; background: #fcf9e8;" onclick="mostrarAba('analisador')">
            <i class="fas fa-microscope" style="color:#D4B31A;"></i> 10. Analisador em Massa
        </button>"""

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - nav button updated")
else:
    print("NOT FOUND")
    idx = content.find('btn-aba-analisador')
    print(repr(content[idx:idx+200]))
