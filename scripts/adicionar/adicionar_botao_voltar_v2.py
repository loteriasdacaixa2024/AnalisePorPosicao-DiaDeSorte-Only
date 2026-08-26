import os
import re

templates_analise = [
    'templates/analise_atrasados.html',
    'templates/analise_meses.html',
    'templates/analise_combinacoes.html',
    'templates/analise_quentes_frios.html'
]

def adicionar_botao_voltar(arquivo):
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    if 'Voltar' in conteudo and 'btn-secondary' in conteudo:
        print(f"⚠️  Botão Voltar já existe em: {arquivo}")
        return False
    
    padrao = r'(<div class="d-flex justify-content-between align-items-center">[\s\S]*?</h2>[\s\S]*?</div>)'
    
    def substituir(match):
        bloco_original = match.group(1)
        
        if 'btn btn-primary' in bloco_original:
            return bloco_original
        
        botao_voltar = '''
                <a href="/" class="btn btn-secondary">
                    <i class="bi bi-arrow-left"></i> Voltar
                </a>'''
        
        novo_bloco = bloco_original.replace('</h2>', '</h2>' + botao_voltar)
        
        return novo_bloco
    
    conteudo_novo = re.sub(padrao, substituir, conteudo)
    
    if conteudo_novo != conteudo:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        print(f"✅ Botão Voltar adicionado em: {arquivo}")
        return True
    else:
        print(f"⚠️  Não foi possível adicionar botão em: {arquivo}")
        return False

print("🚀 Iniciando adição de botões Voltar (versão 2)...\n")

total = 0
sucesso = 0

for template in templates_analise:
    total += 1
    if adicionar_botao_voltar(template):
        sucesso += 1

print(f"\n{'='*50}")
print(f"📊 Resumo: {sucesso}/{total} templates atualizados!")
print(f"{'='*50}")