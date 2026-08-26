content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

# The bug: \\\\n becomes literal \\n in the file instead of a real newline
old = (
    "    globalFatApostas.forEach(ap => {\n"
    "            let nums = ap.dezenas.map(x => x.toString().padStart(2, '0')).join(' ');\n"
    "            conteudo += `${nums} ${ap.mes_nome || 'Jan'}\\\\\\\\n`;\n"
    "        });"
)
new = (
    "    globalFatApostas.forEach(ap => {\n"
    "            let nums = ap.dezenas.map(x => x.toString().padStart(2, '0')).join(' ');\n"
    "            // Abbreviate month to 3 chars (Jan, Fev, Mar...)\n"
    "            let mesAbrev = (ap.mes_nome || 'Jan').substring(0, 3);\n"
    "            conteudo += nums + ' ' + mesAbrev + '\\r\\n';\n"
    "        });"
)

if old in content:
    content = content.replace(old, new, 1)
    open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
    print("OK")
else:
    # Try to find and show what's there
    idx = content.find('function exportarFatiamentoTXT')
    print("NOT FOUND. Current function:")
    print(repr(content[idx:idx+400]))
