import os
import re

templates_analise = [
    'templates/analise_atrasados.html',
    'templates/analise_meses.html',
    'templates/analise_combinacoes.html',
    'templates/analise_quentes_frios.html',
    'templates/analise_pares_impares.html'
]

print("🔍 Analisando estrutura dos botões...\n")

for template in templates_analise:
    if not os.path.exists(template):
        print(f"❌ {template} - NÃO ENCONTRADO")
        continue
    
    with open(template, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    print(f"\n{'='*60}")
    print(f"📄 {template}")
    print('='*60)
    
    padrao_botao = re.search(r'<button[^>]*class="btn btn-primary"[^>]*>.*?</button>', conteudo, re.DOTALL)
    
    if padrao_botao:
        print("Botão encontrado:")
        print(padrao_botao.group(0)[:200])
    else:
        print("⚠️  Nenhum botão btn-primary encontrado")
    
    if 'Voltar' in conteudo:
        print("✅ Já possui botão Voltar")
    else:
        print("❌ NÃO possui botão Voltar")

print(f"\n{'='*60}")