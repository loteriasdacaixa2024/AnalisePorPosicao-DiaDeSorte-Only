content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# The Raio-X header has "background-color: #D4B31A; color: #2d2606;;" - double semicolon, but that's minor
# Let's look for the mostrarAba function and check if it has the geradoresTabsContent div
# The issue might be that geradoresTabsContent div was never found properly

# Check the JS mostrarAba function structure
idx = content.find('function mostrarAba')
func_body = content[idx:idx+3000]
print("mostrarAba function:")
print(func_body[:2000])
