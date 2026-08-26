import os
import re

templates_analise = [
    'templates/analise_atrasados.html',
    'templates/analise_meses.html',
    'templates/analise_combinacoes.html',
    'templates/analise_quentes_frios.html',
    'templates/analise_pares_impares.html'
]

def adicionar_botao_voltar(arquivo):
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo não encontrado: {arquivo}")
        return False
    
    with open(arquivo, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    
    if 'btn-secondary' in conteudo and 'Voltar' in conteudo:
        print(f"⚠️  Botão Voltar já existe em: {arquivo}")
        return False
    
    padrao = r'(<button class="btn btn-primary" onclick="carregarAnalise\(\)">)'
    
    botao_voltar = r'''<a href="/" class="btn btn-secondary me-2">
                    <i class="bi bi-arrow-left"></i> Voltar
                </a>
                \1'''
    
    conteudo_novo = re.sub(padrao, botao_voltar, conteudo)
    
    if conteudo_novo == conteudo:
        padrao_alternativo = r'(<button class="btn btn-primary" onclick="carregarCombinacoes\(\)">)'
        conteudo_novo = re.sub(padrao_alternativo, botao_voltar.replace('carregarAnalise', 'carregarCombinacoes'), conteudo)
    
    if conteudo_novo == conteudo:
        padrao_alternativo2 = r'(<button class="btn btn-primary" onclick="carregarMeses\(\)">)'
        conteudo_novo = re.sub(padrao_alternativo2, botao_voltar.replace('carregarAnalise', 'carregarMeses'), conteudo)
    
    if conteudo_novo == conteudo:
        padrao_alternativo3 = r'(<button class="btn btn-primary" onclick="carregarAtrasados\(\)">)'
        conteudo_novo = re.sub(padrao_alternativo3, botao_voltar.replace('carregarAnalise', 'carregarAtrasados'), conteudo)
    
    if conteudo_novo != conteudo:
        with open(arquivo, 'w', encoding='utf-8') as f:
            f.write(conteudo_novo)
        print(f"✅ Botão Voltar adicionado em: {arquivo}")
        return True
    else:
        print(f"⚠️  Não foi possível adicionar botão em: {arquivo}")
        return False

print("🚀 Iniciando adição de botões Voltar...\n")

total = 0
sucesso = 0

for template in templates_analise:
    total += 1
    if adicionar_botao_voltar(template):
        sucesso += 1

print(f"\n{'='*50}")
print(f"📊 Resumo: {sucesso}/{total} templates atualizados com sucesso!")
print(f"{'='*50}")