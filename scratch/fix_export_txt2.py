content = open('templates/gerador_especial.html', 'r', encoding='utf-8').read()

idx = content.find('function exportarFatiamentoTXT')
idx_end = content.find('\n    }', idx) + 6

print("Current block:")
print(repr(content[idx:idx_end]))
print("---")

old_block = content[idx:idx_end]

new_block = """function exportarFatiamentoTXT() {
        if (!globalFatApostas || globalFatApostas.length === 0) return;
        let linhas = [];
        globalFatApostas.forEach(ap => {
            let nums = ap.dezenas.map(x => x.toString().padStart(2, '0')).join(' ');
            let mesAbrev = (ap.mes_nome || 'Jan').substring(0, 3);
            linhas.push(nums + ' ' + mesAbrev);
        });
        let conteudo = linhas.join('\\r\\n') + '\\r\\n';
        
        let blob = new Blob([conteudo], { type: 'text/plain' });
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.href = url;
        a.download = 'Matriz_Associativa.txt';
        a.click();
        window.URL.revokeObjectURL(url);
    }"""

content = content[:idx] + new_block + content[idx_end:]
open('templates/gerador_especial.html', 'w', encoding='utf-8').write(content)
print("OK - function replaced")
