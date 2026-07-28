content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# Fix 1: JS lookup - all groups now use 'fat_dig_' + k (including gemeas)
old_js = "    const inputId = k === 'gemeas' ? 'fat_gemeas' : 'fat_dig_' + k;"
new_js = "    const inputId = 'fat_dig_' + k;"

if old_js in content:
    content = content.replace(old_js, new_js, 1)
    print("JS fix OK")
else:
    print("JS NOT FOUND")

# Fix 2: also fix the old exportarFatiamentoTXT / enviarFatParaConferencia etc
# that still reference document.getElementById('fat_gemeas')
# These are in other functions so we need to fix them too
count = content.count("getElementById('fat_gemeas')")
print(f"Remaining fat_gemeas references: {count}")
if count > 0:
    content = content.replace("getElementById('fat_gemeas')", "getElementById('fat_dig_gemeas')", count)
    print(f"Fixed {count} remaining references")

open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
print("Done")
