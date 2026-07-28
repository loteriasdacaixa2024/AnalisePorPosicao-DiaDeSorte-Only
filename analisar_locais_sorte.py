import os
import csv
import glob
import re
from datetime import datetime

PASTA_DADOS = r"D:\Loterias\AnalisePorPosicao-DiaDeSorte-Only\conferencias-locais-da-sorte"

def limpar_valor_monetario(valor_str):
    """Converte 'R$ 168.170.026,00' ou similar em um número float"""
    if not valor_str:
        return 0.0
    # Remove R$, espaços, e pontos de milhar, substitui vírgula decimal por ponto
    limpo = valor_str.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        return 0.0

def formatar_moeda(valor):
    """Formata um valor float de volta para o padrão brasileiro R$"""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def obter_arquivos_csv():
    """Lista todos os arquivos CSV na pasta de dados, ordenados por modificação recente"""
    caminho_busca = os.path.join(PASTA_DADOS, "*.csv")
    arquivos = glob.glob(caminho_busca)
    # Ordena pelo tempo de modificação (mais recentes primeiro)
    arquivos.sort(key=os.path.getmtime, reverse=True)
    return arquivos

def analisar_arquivo(caminho_csv):
    print(f"\n[+] Lendo e processando: {os.path.basename(caminho_csv)}...")
    
    stats_cidades = {}
    stats_lotericas = {}
    stats_faixas = {}
    stats_tipo_aposta = {"Simples": {"apostas": 0, "premios_total": 0.0}, "Bolão": {"apostas": 0, "premios_total": 0.0}}
    
    total_linhas_processadas = 0
    total_premios = 0.0
    
    with open(caminho_csv, mode='r', encoding='utf-8') as f:
        # Tenta ler a primeira linha para identificar o delimitador
        primeira_linha = f.readline()
        f.seek(0)
        
        delimitador = ';'
        if ',' in primeira_linha and ';' not in primeira_linha:
            delimitador = ','
            
        reader = csv.DictReader(f, delimiter=delimitador)
        
        # Validação simples de colunas
        campos_esperados = ["Cidade", "Unidade Lotérica", "Faixa de acertos", "Tipo de Aposta", "Prêmio"]
        campos_arquivo = reader.fieldnames if reader.fieldnames else []
        
        # Mapeamento caso os nomes variem levemente
        mapa_colunas = {}
        for campo in campos_esperados:
            for campo_arq in campos_arquivo:
                if campo.lower() in campo_arq.lower():
                    mapa_colunas[campo] = campo_arq
                    break
        
        # Se não mapeou colunas mínimas, avisa
        if len(mapa_colunas) < 3:
            print("[-] Erro: As colunas do CSV não parecem conter os dados necessários para análise.")
            print(f"Colunas encontradas: {campos_arquivo}")
            return
            
        col_cidade = mapa_colunas.get("Cidade", "Cidade")
        col_loterica = mapa_colunas.get("Unidade Lotérica", "Unidade Lotérica")
        col_faixa = mapa_colunas.get("Faixa de acertos", "Faixa de acertos")
        col_tipo = mapa_colunas.get("Tipo de Aposta", "Tipo de Aposta")
        col_premio = mapa_colunas.get("Prêmio", "Prêmio")
        col_qtd_premios = "Quantidade de prêmios por faixa" # nome padrão da Caixa
        
        # Se a coluna de quantidade de prêmios por faixa não existir de forma exata, tenta buscar similar
        for col in campos_arquivo:
            if "quantidade" in col.lower() and "faixa" in col.lower():
                col_qtd_premios = col
                break
        
        for idx, row in enumerate(reader, start=1):
            cidade = row.get(col_cidade, "DESCONHECIDO").strip().upper()
            loterica = row.get(col_loterica, "DESCONHECIDO").strip().upper()
            faixa = row.get(col_faixa, "DESCONHECIDO").strip()
            tipo = row.get(col_tipo, "Simples").strip()
            premio_str = row.get(col_premio, "0")
            
            # Limpa/Corrige tipo de aposta
            if "bol" in tipo.lower():
                tipo_limpo = "Bolão"
            else:
                tipo_limpo = "Simples"
                
            qtd_premios = 1
            if col_qtd_premios in row:
                try:
                    qtd_premios = int(row[col_qtd_premios].strip())
                except:
                    qtd_premios = 1
            
            premio_float = limpar_valor_monetario(premio_str)
            total_premios += premio_float
            total_linhas_processadas += 1
            
            # --- Estatísticas por Cidade ---
            if cidade not in stats_cidades:
                stats_cidades[cidade] = {"total_apostas": 0, "premios_total": 0.0, "faixas": {}}
            stats_cidades[cidade]["total_apostas"] += qtd_premios
            stats_cidades[cidade]["premios_total"] += premio_float
            
            if faixa not in stats_cidades[cidade]["faixas"]:
                stats_cidades[cidade]["faixas"][faixa] = 0
            stats_cidades[cidade]["faixas"][faixa] += qtd_premios
            
            # --- Estatísticas por Lotérica (associando à cidade para evitar colisões de nome) ---
            chave_loterica = f"{loterica} ({cidade})"
            if chave_loterica not in stats_lotericas:
                stats_lotericas[chave_loterica] = {"total_apostas": 0, "premios_total": 0.0, "cidade": cidade, "nome": loterica}
            stats_lotericas[chave_loterica]["total_apostas"] += qtd_premios
            stats_lotericas[chave_loterica]["premios_total"] += premio_float
            
            # --- Estatísticas por Faixa ---
            if faixa not in stats_faixas:
                stats_faixas[faixa] = {"total_apostas": 0, "premios_total": 0.0}
            stats_faixas[faixa]["total_apostas"] += qtd_premios
            stats_faixas[faixa]["premios_total"] += premio_float
            
            # --- Estatísticas por Tipo de Aposta ---
            if tipo_limpo not in stats_tipo_aposta:
                stats_tipo_aposta[tipo_limpo] = {"apostas": 0, "premios_total": 0.0}
            stats_tipo_aposta[tipo_limpo]["apostas"] += qtd_premios
            stats_tipo_aposta[tipo_limpo]["premios_total"] += premio_float
            
    # Processamento Final das Listas Ordenadas
    top_cidades_apostas = sorted(stats_cidades.items(), key=lambda x: x[1]["total_apostas"], reverse=True)
    top_cidades_financeiro = sorted(stats_cidades.items(), key=lambda x: x[1]["premios_total"], reverse=True)
    
    top_lotericas_apostas = sorted(stats_lotericas.items(), key=lambda x: x[1]["total_apostas"], reverse=True)
    top_lotericas_financeiro = sorted(stats_lotericas.items(), key=lambda x: x[1]["premios_total"], reverse=True)
    
    # Exibe resumo no terminal
    print("\n" + "="*70)
    print("  RESULTADOS DA ANÁLISE DOS LOCAIS DA SORTE  ".center(70, "="))
    print("="*70)
    print(f"Total de bilhetes premiados analisados: {total_linhas_processadas}")
    print(f"Total pago em prêmios no arquivo: {formatar_moeda(total_premios)}")
    print("-"*70)
    
    print("\n[+] TOP 5 CIDADES COM MAIS BILHETES PREMIADOS (Qtd. de Apostas):")
    for i, (cid, dados) in enumerate(top_cidades_apostas[:5], 1):
        print(f"  {i}º. {cid} - {dados['total_apostas']} apostas ganharam ({formatar_moeda(dados['premios_total'])})")
        
    print("\n[+] TOP 5 CIDADES POR VOLUME FINANCEIRO DE PRÊMIOS:")
    for i, (cid, dados) in enumerate(top_cidades_financeiro[:5], 1):
        print(f"  {i}º. {cid} - {formatar_moeda(dados['premios_total'])} em prêmios ({dados['total_apostas']} apostas)")
        
    print("\n[+] TOP 5 LOTÉRICAS COM MAIS BILHETES PREMIADOS:")
    for i, (lot, dados) in enumerate(top_lotericas_apostas[:5], 1):
        print(f"  {i}º. {dados['nome']} em {dados['cidade']} - {dados['total_apostas']} apostas ganharam")
        
    print("\n[+] DISTRIBUIÇÃO POR TIPO DE APOSTA:")
    for tipo, dados in stats_tipo_aposta.items():
        percent_apostas = (dados["apostas"] / sum(d["apostas"] for d in stats_tipo_aposta.values()) * 100) if sum(d["apostas"] for d in stats_tipo_aposta.values()) > 0 else 0
        print(f"  [{tipo}] {dados['apostas']} apostas premiadas ({percent_apostas:.1f}%) - Total: {formatar_moeda(dados['premios_total'])}")
        
    print("\n[+] PREMIAÇÕES POR FAIXA DE ACERTO:")
    for faixa, dados in stats_faixas.items():
        print(f"  - {faixa}: {dados['total_apostas']} apostas - Total pago: {formatar_moeda(dados['premios_total'])}")
        
    # Geração do Relatório em Markdown (Lindo e Profissional)
    nome_base = os.path.basename(caminho_csv).replace(".csv", "")
    caminho_relatorio = os.path.join(PASTA_DADOS, f"relatorio_analise_{nome_base}.md")
    
    with open(caminho_relatorio, "w", encoding="utf-8") as rf:
        rf.write(f"# Relatório de Análise - Locais da Sorte ({nome_base})\n\n")
        rf.write(f"Gerado automaticamente em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
        rf.write(f"Arquivo analisado: `{os.path.basename(caminho_csv)}`\n\n")
        
        rf.write("## 📊 Visão Geral dos Resultados\n\n")
        rf.write(f"- **Total de bilhetes premiados analisados:** {total_linhas_processadas}\n")
        rf.write(f"- **Volume total acumulado de prêmios:** `{formatar_moeda(total_premios)}`\n\n")
        
        rf.write("### 🎟️ Simples vs. Bolão\n")
        rf.write("| Tipo de Aposta | Qtd. de Apostas Premiadas | % de Participação | Total Acumulado Pago |\n")
        rf.write("| :--- | :---: | :---: | :---: |\n")
        total_apos = sum(d["apostas"] for d in stats_tipo_aposta.values())
        for tipo, dados in stats_tipo_aposta.items():
            pct = (dados["apostas"] / total_apos * 100) if total_apos > 0 else 0
            rf.write(f"| {tipo} | {dados['apostas']} | {pct:.1f}% | {formatar_moeda(dados['premios_total'])} |\n")
            
        rf.write("\n### 🎯 Premiações por Faixa de Acerto\n")
        rf.write("| Faixa de Acertos | Qtd. de Apostas Premiadas | Total Acumulado Pago |\n")
        rf.write("| :--- | :---: | :---: |\n")
        for faixa, dados in sorted(stats_faixas.items(), key=lambda x: x[0]):
            rf.write(f"| {faixa} | {dados['total_apostas']} | {formatar_moeda(dados['premios_total'])} |\n")
            
        rf.write("\n## 🏙️ Ranking por Cidade\n\n")
        rf.write("Abaixo estão as 15 cidades que mais registraram apostas premiadas neste concurso:\n\n")
        rf.write("| Posição | Cidade/Estado | Qtd. Apostas Premiadas | Total Pago na Cidade | Prêmios por Faixa |\n")
        rf.write("| :---: | :--- | :---: | :---: | :--- |\n")
        for idx, (cid, dados) in enumerate(top_cidades_apostas[:15], 1):
            faixas_str = ", ".join([f"{f}: {q}" for f, q in sorted(dados["faixas"].items())])
            rf.write(f"| **{idx}º** | {cid} | {dados['total_apostas']} | {formatar_moeda(dados['premios_total'])} | {faixas_str} |\n")
            
        rf.write("\n## 🏪 Ranking das Unidades Lotéricas\n\n")
        rf.write("As 15 lotéricas com maior frequência de bilhetes premiados:\n\n")
        rf.write("| Posição | Unidade Lotérica | Cidade/Estado | Qtd. Apostas Premiadas | Total Acumulado Pago |\n")
        rf.write("| :---: | :--- | :--- | :---: | :---: |\n")
        for idx, (chave, dados) in enumerate(top_lotericas_apostas[:15], 1):
            rf.write(f"| **{idx}º** | {dados['nome']} | {dados['cidade']} | {dados['total_apostas']} | {formatar_moeda(dados['premios_total'])} |\n")
            
        rf.write("\n## 🧠 Análise Crítica e Matemática (Fator Estatístico vs. Sorte)\n\n")
        rf.write("> [!NOTE]\n")
        rf.write("> **Por que cidades como São Paulo, Rio de Janeiro e Brasília aparecem sempre no topo?**\n")
        rf.write("> Isso ocorre devido à **Lei dos Grandes Números** e à densidade populacional. Como essas cidades vendem dezenas de milhões de bilhetes a mais que cidades menores, estatisticamente elas sempre concentrarão o maior número de ganhadores.\n")
        rf.write(">\n")
        rf.write("> **Onde comprar meu jogo?**\n")
        rf.write("> 1. **Probabilidade Individual:** A chance de um bilhete simples (6 dezenas na Mega-Sena) ganhar é sempre de **1 em 50.063.860**, seja ele comprado na lotérica mais famosa de São Paulo ou em um vilarejo no interior.\n")
        rf.write("> 2. **A real vantagem dos Bolões das 'Lotéricas Pé Quente':** A principal vantagem de comprar bolões elaborados em lotéricas grandes ou famosas não é a \"energia\" do local, mas sim o fato de elas montarem **jogos estruturados de 10 a 20 números por bilhete** (o que seria financeiramente inviável de jogar sozinho). Participar de um bolão de 15 dezenas (equivalente a 5.005 apostas) aumenta de forma monstruosa suas chances matemáticas de premiação real (6, 5 ou 4 acertos).\n")
        
    print(f"\n[+] Relatório Markdown salvo com sucesso em:\n    {caminho_relatorio}")
    print("="*70 + "\n")

def main():
    print("="*60)
    print("  Analisador de Locais da Sorte (Estatísticas e Rankings) ")
    print("="*60)
    
    arquivos = obter_arquivos_csv()
    if not arquivos:
        print("[-] Nenhum arquivo de dados CSV encontrado na pasta:")
        print(f"    {PASTA_DADOS}")
        print("[!] Por favor, execute o script de extração 'extrair_locais_sorte.py' primeiro!")
        return
        
    print(f"[+] Encontrado(s) {len(arquivos)} arquivo(s) de extração:")
    for idx, arq in enumerate(arquivos, 1):
        nome = os.path.basename(arq)
        mtime = os.path.getmtime(arq)
        data_mod = datetime.fromtimestamp(mtime).strftime('%d/%m/%Y %H:%M:%S')
        tamanho = os.path.getsize(arq) / 1024
        print(f"  [{idx}] {nome} ({data_mod}) - {tamanho:.1f} KB")
        
    escolha = input(f"\nDigite o número do arquivo que deseja analisar (ou ENTER para o mais recente [1]): ").strip()
    
    if not escolha:
        caminho_selecionado = arquivos[0]
    else:
        try:
            opcao = int(escolha)
            if 1 <= opcao <= len(arquivos):
                caminho_selecionado = arquivos[opcao - 1]
            else:
                print("[-] Opção inválida. Analisando o arquivo mais recente por padrão.")
                caminho_selecionado = arquivos[0]
        except ValueError:
            print("[-] Entrada inválida. Analisando o arquivo mais recente por padrão.")
            caminho_selecionado = arquivos[0]
            
    analisar_arquivo(caminho_selecionado)

if __name__ == "__main__":
    main()
