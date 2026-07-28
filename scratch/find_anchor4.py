content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# The <script> tag is actually inline style before the main script block
# Let's find the MAIN script - the one with mostrarAba function
idx_mostrarab = content.find('function mostrarAba')
print("mostrarAba at:", idx_mostrarab)

# The script tag for the main JS block
idx_main_script = content.rfind('<script>', 0, idx_mostrarab)
print("Main script tag at:", idx_main_script)

# Before the main script tag, there should be the closing divs
print("Before main script:")
print(repr(content[idx_main_script-300:idx_main_script+20]))
