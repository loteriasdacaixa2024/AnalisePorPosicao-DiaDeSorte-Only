content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

old = """        let fatiamentoEl = document.getElementById('fatiamento');
        if (fatiamentoEl) fatiamentoEl.style.display = (aba === 'fatiamento') ? 'block' : 'none';


        let batalhaEl = document.getElementById('batalha');"""

new = """        let fatiamentoEl = document.getElementById('fatiamento');
        if (fatiamentoEl) fatiamentoEl.style.display = (aba === 'fatiamento') ? 'block' : 'none';

        let analisadorEl = document.getElementById('analisador');
        if (analisadorEl) analisadorEl.style.display = (aba === 'analisador') ? 'block' : 'none';

        let batalhaEl = document.getElementById('batalha');"""

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - analisador registered in mostrarAba")
else:
    print("NOT FOUND")
