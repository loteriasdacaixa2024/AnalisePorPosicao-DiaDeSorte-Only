content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Find the mostrarAba function - it has a list of aba ids
# Look for where 'fatiamento' is mentioned in the aba list
idx = content.find("'fatiamento'", content.find('function mostrarAba'))
print("fatiamento in mostrarAba at:", idx)
print(repr(content[idx-200:idx+300]))
