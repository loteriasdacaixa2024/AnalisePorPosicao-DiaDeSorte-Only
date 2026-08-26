import os
import re

templates_analise = [
    'templates/analise_atrasados.html',
]

print("🔍 Analisando estrutura HTML...\n")

for template in templates_analise:
    if not os.path.exists(template):
        print(f"❌ {template} - NÃO ENCONTRADO")
        continue
    
    with open(template, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print(f"{'='*60}")
    print(f"📄 {template}")
    print('='*60)
    
    padrao_header = re.search(r'<div class="row mb-4">[\s\S]{0,800}?</div>[\s\S]{0,100}?</div>', conteudo)
    
    if padrao_header:
        print("ESTRUTURA DO CABEÇALHO:")
        print(padrao_header.group(0))
    else:
        inicio = conteudo.find('<div class="container')
        if inicio != -1:
            print("PRIMEIROS 1000 CARACTERES APÓS CONTAINER:")
            print(conteudo[inicio:inicio+1000])

print(f"\n{'='*60}")