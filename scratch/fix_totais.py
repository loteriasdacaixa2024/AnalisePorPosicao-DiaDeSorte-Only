content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# The bug: after building totaisHtml, it goes straight to TOP 3 ESPALHADOS
# without doing getElementById('placard_totais').innerHTML = totaisHtml
old = "                    });\n                    // --- TOP 3 SORTEIOS MAIS ESPALHADOS ---"
new = ("                    });\n"
       "                    const placardTotais = document.getElementById('placard_totais');\n"
       "                    if (placardTotais) placardTotais.innerHTML = totaisHtml;\n\n"
       "                    // --- TOP 3 SORTEIOS MAIS ESPALHADOS ---")

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK - fixed missing placardTotais assignment")
else:
    print("NOT FOUND")
    idx = content.find('totaisHtml += `')
    print(repr(content[idx+400:idx+600]))
