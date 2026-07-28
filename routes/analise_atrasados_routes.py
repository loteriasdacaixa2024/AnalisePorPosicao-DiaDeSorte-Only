from flask import Blueprint, jsonify, request, render_template
from services.analise_atrasados_service import AnaliseAtrasadosService
from services.analise_afinidade_service import AnaliseAfinidadeService
from services.analise_soma_dezenas_service import AnaliseSomaDezenasService
from services.analise_digitos_unicos_service import AnaliseDigitosUnicosService
from services.analise_sequencias_service import AnaliseSequenciasService

analise_atrasados_bp = Blueprint('analise_atrasados', __name__)

@analise_atrasados_bp.route('/api/analise/atrasados/posicao/<int:posicao>', methods=['GET'])
def obter_atrasados_por_posicao(posicao):
    top = request.args.get('top', 10, type=int)
    modo = request.args.get('modo', 'crescente')
    resultado = AnaliseAtrasadosService.obter_frequencia_por_posicao(posicao, modo=modo)
    
    if 'erro' in resultado:
        return jsonify(resultado), 400
    
    return jsonify(resultado)

@analise_atrasados_bp.route('/api/analise/ultimos-dois-concursos', methods=['GET'])
def obter_ultimos_dois_concursos():
    from models.sorteio import Sorteio
    from models.shared import db
    try:
        sorteios = db.session.query(Sorteio).order_by(Sorteio.concurso.desc()).limit(2).all()
        if not sorteios:
            return jsonify({"erro": "Nenhum sorteio encontrado"}), 404
            
        resultado = []
        for s in sorteios:
            dezenas = [s.posicao_1, s.posicao_2, s.posicao_3, s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7]
            resultado.append({
                "concurso": s.concurso,
                "dezenas": dezenas
            })
        return jsonify(resultado)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@analise_atrasados_bp.route('/api/analise/ultimo-concurso', methods=['GET'])
def obter_ultimo_concurso():
    from models.sorteio import Sorteio
    ultimo = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
    if not ultimo:
        return jsonify({"erro": "Nenhum sorteio encontrado"}), 404
        
    dezenas = [ultimo.posicao_1, ultimo.posicao_2, ultimo.posicao_3, ultimo.posicao_4, ultimo.posicao_5, ultimo.posicao_6, ultimo.posicao_7]
    return jsonify({
        "concurso": ultimo.concurso,
        "dezenas": dezenas
    })

@analise_atrasados_bp.route('/api/analise/atrasados/probabilidade/<int:concursos>', methods=['GET'])
def calcular_probabilidade(concursos):
    prob = AnaliseAtrasadosService.calcular_probabilidade(concursos)
    return jsonify({
        'concursos': concursos,
        'probabilidade': prob
    })

def get_meses_atrasados():
    from sqlalchemy import text
    from models.shared import db
    sql = text("""
        SELECT mes_sorte, MAX(concurso) as ultimo_conc
        FROM sorteios
        WHERE mes_sorte IS NOT NULL AND mes_sorte >= 1 AND mes_sorte <= 12
        GROUP BY mes_sorte
        ORDER BY ultimo_conc ASC
    """)
    rows = db.session.execute(sql).fetchall()
    meses_encontrados = {row[0] for row in rows}
    meses_nunca = [m for m in range(1, 13) if m not in meses_encontrados]
    ranking = meses_nunca + [row[0] for row in rows]
    return ranking if ranking else [1]


@analise_atrasados_bp.route('/analise/numeros-atrasados')
def pagina_numeros_atrasados():
    return render_template('analise_atrasados.html')

@analise_atrasados_bp.route('/api/analise/atrasados/gerar-apostas', methods=['POST'])
def gerar_apostas_atrasados():
    data = request.json or {}
    modo = data.get('modo', 'sorteio')
    top_n = data.get('top_n', 3)
    qtd_jogos = data.get('qtd_jogos', 30)
    modo_mes = data.get('modo_mes', 'ranking_atraso')
    soma_min = data.get('soma_min', 37)
    soma_max = data.get('soma_max', 135)
    digitos_min = data.get('digitos_min', 5)
    digitos_max = data.get('digitos_max', 8)
    max_seq = data.get('max_seq', 3)
    
    all_per_pos = {}
    for pos in range(1, 8):
        res = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo=modo)
        if 'erro' in res:
            return jsonify(res), 400
        all_per_pos[pos] = [item['numero'] for item in res['numeros']]

    import itertools
    valid_games = set()
    
    # Incrementa progressivamente a cobertura "top_n" até obter boas combinações exclusivas (contorna overlaps de atraso de 1200)
    limite = top_n
    MAX_GAMES = 2000
    
    while limite <= 12:
        pools = [all_per_pos[p][:limite] for p in range(1, 8)]
        for game in itertools.product(*pools):
            if len(set(game)) == 7:
                s_game = sorted(game)

                soma = sum(s_game)
                if soma < soma_min or soma > soma_max: continue

                digits = set()
                for n in s_game:
                    digits.add(n // 10)
                    digits.add(n % 10)
                if len(digits) < digitos_min or len(digits) > digitos_max: continue

                # Filtro Anti-Aberração Progressivo
                tem_seq = False
                for idx in range(len(s_game) - max_seq):
                    if s_game[idx+max_seq] - s_game[idx] == max_seq:
                        tem_seq = True
                        break
                if not tem_seq:
                    valid_games.add(tuple(s_game))
                    if len(valid_games) >= MAX_GAMES:
                        break
        if len(valid_games) >= 50 or limite == 12:
            break
        limite += 1
            
    from models.sorteio import Sorteio
    todos_sorteios = Sorteio.query.all()
    sorteios_historicos = {
        tuple(sorted([s.posicao_1, s.posicao_2, s.posicao_3, s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7]))
        for s in todos_sorteios
    }

    # Remove apostas que já saíram na história
    valid_games_ineditos = []
    apostas_descartadas_historico = 0
    for g in valid_games:
        if g not in sorteios_historicos:
            valid_games_ineditos.append(g)
        else:
            apostas_descartadas_historico += 1
            
    valid_games = valid_games_ineditos[:qtd_jogos]
    
    import os
    import time
    from flask import current_app
    import threading
    from models.shared import db
    from services.conferencia_historica_service import ConferenciaHistoricaService
    
    filename = "SniperVertical.txt"
    filepath = os.path.join(os.getcwd(), 'conferencia_filtros-baixados', filename)
    
    from services.analise_meses_service import AnaliseMesesService
    stats_meses = AnaliseMesesService.obter_estatisticas_meses()
    meses_ordenados = stats_meses['meses']
    
    # Lógica de Distribuição Profissional (24 ciclo + 6 extremos)
    meses_ciclo_total = list(range(1, 13)) + list(range(1, 13))
    stats_meses = AnaliseMesesService.obter_estatisticas_meses()
    meses_ordenados = stats_meses['meses']
    top_3_atraso = [m['numero'] for m in meses_ordenados[:3]]
    meses_por_freq = sorted(meses_ordenados, key=lambda x: x['frequencia'], reverse=True)
    top_3_freq = [m['numero'] for m in meses_por_freq[:3]]
    meses_final_30 = meses_ciclo_total + top_3_atraso + top_3_freq

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        for i, g in enumerate(valid_games):
            if i < len(meses_final_30):
                mes = meses_final_30[i]
            else:
                mes = meses_final_30[i % len(meses_final_30)]
            
            mes_nome = AnaliseMesesService.obter_nome_mes(mes)
            f.write(" ".join(f"{x:02d}" for x in g) + f" {mes_nome}\n")
            
    msg_filtros = f" (Filtros: Soma {soma_min}-{soma_max}, Dígitos {digitos_min}-{digitos_max}, Seq Máx {max_seq})"
    msg_extra = f" ({apostas_descartadas_historico} descartadas por já terem saído no histórico)" if apostas_descartadas_historico > 0 else ""
    
    return jsonify({
        'sucesso': True,
        'arquivo_gerado': filename,
        'caminho': filepath,
        'total_combinacoes': len(valid_games),
        'mensagem': f'{len(valid_games)} apostas inéditas geradas com sucesso!{msg_filtros}{msg_extra}'
    })

@analise_atrasados_bp.route('/api/analise/atrasados/gerar-rank-vertical', methods=['POST'])
def gerar_rank_vertical():
    data = request.json or {}
    modo = data.get('modo', 'sorteio')
    qtd = data.get('qtd_apostas', 5)
    modo_mes = data.get('modo_mes', 'ranking_atraso')
    soma_min = data.get('soma_min', 37)
    soma_max = data.get('soma_max', 135)
    digitos_min = data.get('digitos_min', 5)
    digitos_max = data.get('digitos_max', 8)
    max_seq = data.get('max_seq', 3)
    
    all_per_pos = {}
    for pos in range(1, 8):
        res = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo=modo)
        if 'erro' in res:
            return jsonify(res), 400
        all_per_pos[pos] = [item['numero'] for item in res['numeros']]
        
    valid_games = []
    
    # Busca iterativamente até preencher a cota ou bater no máximo de exploração razoável (100)
    for i in range(100):
        bet = []
        for p in range(1, 8):
            ranking_list = all_per_pos[p]
            offset = 0
            # Target = i (onde 0 é o Top 1, 1 é o Top 2, etc.)
            target_idx = i
            while offset < len(ranking_list):
                candidato = ranking_list[(target_idx + offset) % len(ranking_list)]
                if candidato not in bet:
                    bet.append(candidato)
                    break
                offset += 1
                
        if len(bet) == 7:
            s_game = sorted(bet)
            soma = sum(s_game)
            if soma < soma_min or soma > soma_max: continue

            digits = set()
            for n in s_game:
                digits.add(n // 10)
                digits.add(n % 10)
            if len(digits) < digitos_min or len(digits) > digitos_max: continue

            tem_seq = False
            for idx in range(len(s_game) - max_seq):
                if s_game[idx+max_seq] - s_game[idx] == max_seq:
                    tem_seq = True
                    break
            if not tem_seq:
                valid_games.append(s_game)
            
            if len(valid_games) >= qtd: break
    from models.sorteio import Sorteio
    todos_sorteios = Sorteio.query.all()
    sorteios_historicos = {
        tuple(sorted([s.posicao_1, s.posicao_2, s.posicao_3, s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7]))
        for s in todos_sorteios
    }

    valid_games_ineditos = []
    apostas_descartadas_historico = 0
    for g in valid_games:
        if tuple(g) not in sorteios_historicos:
            valid_games_ineditos.append(g)
        else:
            apostas_descartadas_historico += 1
            
    valid_games = valid_games_ineditos

    import os
    import time
    from flask import current_app
    import threading
    from models.shared import db
    from services.conferencia_historica_service import ConferenciaHistoricaService
    
    # Unificando pasta para /conferencia_filtros-baixados
    save_dir = os.path.join(os.getcwd(), 'conferencia_filtros-baixados')
    os.makedirs(save_dir, exist_ok=True)
    
    filename = "SniperVertical.txt"
    filepath = os.path.join(save_dir, filename)
    
    with open(filepath, 'w') as f:
        from services.analise_meses_service import AnaliseMesesService
        stats_meses = AnaliseMesesService.obter_estatisticas_meses()
        meses_ordenados = stats_meses['meses']
        
        # Lógica de Distribuição de Meses (24 cobertura total + 6 extremos estatísticos)
        # 1-12: Jan-Dez
        # 13-24: Jan-Dez
        # 25-27: Top 3 Atrasados
        # 28-30: Top 3 Frequentes
        
        meses_ciclo_total = list(range(1, 13)) + list(range(1, 13)) # 24 meses
        
        # Obter os Extremos (Atrasados e Frequentes)
        stats_meses = AnaliseMesesService.obter_estatisticas_meses()
        meses_ordenados = stats_meses['meses'] # Atraso (desc)
        top_3_atraso = [m['numero'] for m in meses_ordenados[:3]]
        
        meses_por_freq = sorted(meses_ordenados, key=lambda x: x['frequencia'], reverse=True)
        top_3_freq = [m['numero'] for m in meses_por_freq[:3]]
        
        # Lista final de meses para 30 apostas
        meses_final_30 = meses_ciclo_total + top_3_atraso + top_3_freq

        for i, g in enumerate(valid_games):
            # Se for mais de 30, volta a usar o ranking de atraso ou repete o ciclo
            if i < len(meses_final_30):
                mes = meses_final_30[i]
            else:
                mes = meses_final_30[i % len(meses_final_30)]
            
            mes_nome = AnaliseMesesService.obter_nome_mes(mes)
            f.write(" ".join(f"{x:02d}" for x in g) + f" {mes_nome}\n")
            
    msg_extra = f" (⚠️ {apostas_descartadas_historico} descartadas por já terem saído no histórico geral)" if apostas_descartadas_historico > 0 else ""
            
    return jsonify({
        'sucesso': True,
        'arquivo_gerado': filename,
        'caminho': filepath,
        'total_combinacoes': len(valid_games),
        'apostas': valid_games,
        'mensagem': f'{len(valid_games)} apostas "Sniper Absoluto" extraídas com sucesso!' + msg_extra
    })

@analise_atrasados_bp.route('/api/analise/afinidade/clusters', methods=['GET'])
def obter_clusters_afinidade():
    janela = request.args.get('janela', 30, type=int)
    forca = request.args.get('forca', 3, type=int)
    resultado = AnaliseAfinidadeService.obter_clusters_e_hubs(janela=janela, força_minima=forca)
    return jsonify(resultado)

@analise_atrasados_bp.route('/api/analise/afinidade/gerar-apostas', methods=['POST'])
def gerar_apostas_afinidade():
    import os
    import time
    from models.sorteio import Sorteio
    from services.analise_ciclos_dezenas_service import AnaliseCiclosDezenasService
    from services.analise_meses_service import AnaliseMesesService
    
    data = request.json or {}
    janela = data.get('janela', 30)
    forca = data.get('forca', 2)
    qtd_jogos = data.get('qtd_jogos', 50)
    modo_mes = data.get('modo_mes', 'ranking_atraso')
    excluir = data.get('excluir', [])
    dezenas_pendentes_ciclo = data.get('pendentes_ciclo', []) # Recebe do Front interativo
    soma_min = data.get('soma_min', 37)
    soma_max = data.get('soma_max', 135)
    digitos_min = data.get('digitos_min', 5)
    digitos_max = data.get('digitos_max', 8)
    max_seq = data.get('max_seq', 3)
    
    # Pegar o Top Atrasados de TODAS as 7 posições para garantir a mesma base da aba 1
    pool_geracao = set()
    for pos in range(1, 8):
        res_pos = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo='sorteio')
        if 'numeros' in res_pos:
            # Pegamos os top 4 de cada posição
            for item in res_pos['numeros'][:4]:
                pool_geracao.add(item['numero'])
    
    # IMPORTANTE: Adicionar sobreviventes do último concurso (que não foram excluídas)
    ultimo_s = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
    if ultimo_s:
        dezenas_ult = [ultimo_s.posicao_1, ultimo_s.posicao_2, ultimo_s.posicao_3, ultimo_s.posicao_4, ultimo_s.posicao_5, ultimo_s.posicao_6, ultimo_s.posicao_7]
        for d in dezenas_ult:
            if d not in excluir:
                pool_geracao.add(d)
    
    atrasados_base = list(pool_geracao)
    
    # Gerar dezenas por afinidade usando essa base posicional de elite
    gen_res = AnaliseAfinidadeService.gerar_apostas_afinidade(
        top_atrasados_list=atrasados_base,
        janela=janela,
        força_minima=forca,
        qtd_apostas=qtd_jogos,
        excluir_numeros=excluir,
        dezenas_ciclo=dezenas_pendentes_ciclo,
        soma_min=soma_min, soma_max=soma_max, digitos_min=digitos_min, digitos_max=digitos_max, max_seq=max_seq
    )
    
    if not gen_res.get('sucesso'):
        return jsonify(gen_res), 400
        
    apostas_dezenas = gen_res['apostas']
    
    # LÓGICA DE DISTRIBUIÇÃO PROFISSIONAL (24 cobertura total + 6 extremos estatísticos)
    # 12 Jan-Dez + 12 Jan-Dez + 3 Top Atraso + 3 Top Frequent
    meses_ciclo_total = list(range(1, 13)) + list(range(1, 13))
    
    stats_meses = AnaliseMesesService.obter_estatisticas_meses()
    meses_ordenados = stats_meses['meses'] # Atraso (desc)
    top_3_atraso = [m['numero'] for m in meses_ordenados[:3]]
    meses_por_freq = sorted(meses_ordenados, key=lambda x: x['frequencia'], reverse=True)
    top_3_freq = [m['numero'] for m in meses_por_freq[:3]]
    
    meses_final_30 = meses_ciclo_total + top_3_atraso + top_3_freq

    # Gerar as linhas finais com Mês
    linhas_finais = []
    for i, dezenas in enumerate(apostas_dezenas):
        if i < len(meses_final_30):
            mes = meses_final_30[i]
        else:
            mes = meses_final_30[i % len(meses_final_30)]
            
        mes_nome = AnaliseMesesService.obter_nome_mes(mes)
        linha = " ".join(f"{d:02d}" for d in sorted(dezenas)) + f" {mes_nome}"
        linhas_finais.append(linha)
    
    filename = "AfinidadeIA.txt"
    filepath = os.path.join(os.getcwd(), 'conferencia_filtros-baixados', filename)
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        for linha in linhas_finais:
            f.write(linha + "\n")
            
    msg_filtros = f" (Filtros: Soma {soma_min}-{soma_max}, Dígitos {digitos_min}-{digitos_max}, Seq Máx {max_seq})"
    return jsonify({
        'sucesso': True,
        'arquivo_gerado': filename,
        'caminho': filepath,
        'total_combinacoes': len(apostas_dezenas),
        'apostas': apostas_dezenas,
        'mensagem': f'{len(apostas_dezenas)} apostas de afinidade geradas com sucesso!{msg_filtros}'
    })

@analise_atrasados_bp.route('/api/analise/comparativo-diferencial', methods=['POST'])
def obter_comparativo_diferencial():
    data = request.json or {}
    janela = data.get('janela', 30)
    forca = data.get('forca', 3)
    qtd_jogos = data.get('qtd_jogos', 30)
    excluir = data.get('excluir', [])
    pendentes_ciclo = data.get('pendentes_ciclo', [])
    soma_min = data.get('soma_min', 37)
    soma_max = data.get('soma_max', 135)
    digitos_min = data.get('digitos_min', 5)
    digitos_max = data.get('digitos_max', 8)
    max_seq = data.get('max_seq', 3)

    # 1. Obter Sniper Vertical (Atraso Puro)
    sniper_games = AnaliseAtrasadosService.obter_rank_vertical(modo='sorteio', qtd=qtd_jogos)

    # 2. Obter Afinidade (IA)
    pool_geracao = set()
    for pos in range(1, 8):
        res_pos = AnaliseAtrasadosService.obter_frequencia_por_posicao(pos, modo='sorteio')
        if 'numeros' in res_pos:
            for item in res_pos['numeros'][:4]:
                pool_geracao.add(item['numero'])
    
    from models.sorteio import Sorteio
    ultimo_s = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
    if ultimo_s:
        dezenas_ult = [ultimo_s.posicao_1, ultimo_s.posicao_2, ultimo_s.posicao_3, ultimo_s.posicao_4, ultimo_s.posicao_5, ultimo_s.posicao_6, ultimo_s.posicao_7]
        for d in dezenas_ult:
            if d not in excluir:
                pool_geracao.add(d)
    
    atrasados_base = list(pool_geracao)
    
    afinidade_res = AnaliseAfinidadeService.gerar_apostas_afinidade(
        top_atrasados_list=atrasados_base,
        janela=janela,
        força_minima=forca,
        qtd_apostas=qtd_jogos,
        excluir_numeros=excluir,
        dezenas_ciclo=pendentes_ciclo,
        soma_min=soma_min, soma_max=soma_max, digitos_min=digitos_min, digitos_max=digitos_max, max_seq=max_seq
    )
    afinidade_games = afinidade_res.get('apostas', [])

    return jsonify({
        'sucesso': True,
        'apostas': afinidade_games,
        'mensagem': f'{len(afinidade_games)} apostas de afinidade geradas e salvas com sucesso!'
    })

@analise_atrasados_bp.route('/api/analise/comparativo/ultimos-arquivos', methods=['GET'])
def obter_comparativo_ultimos_arquivos():
    import os
    
    save_dir = os.path.join(os.getcwd(), 'conferencia_filtros-baixados')
    if not os.path.exists(save_dir):
        return jsonify({'sucesso': True, 'sniper': [], 'afinidade': []})

    # Listar todos os arquivos da pasta
    try:
        todos_arquivos = os.listdir(save_dir)
    except:
        return jsonify({'sucesso': False, 'mensagem': 'Erro ao acessar pasta de arquivos.'})

    # 1. Filtrar Sniper
    sniper_files = []
    for f in todos_arquivos:
        if f.endswith(".txt") and (
            "NumerosAtrasadoPosicao" in f or 
            "SniperVertical" in f or
            "Top_Atrasados_" in f or 
            "Rank_Vertical_" in f or 
            "Sniper_Vertical_Duelo" in f
        ):
            sniper_files.append(os.path.join(save_dir, f))
    
    latest_sniper_game = []
    latest_s = None
    if sniper_files:
        latest_s = max(sniper_files, key=os.path.getmtime)
        try:
            with open(latest_s, 'r') as f_read:
                for line in f_read:
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        try:
                            game = [int(x) for x in parts[:7]]
                            latest_sniper_game.append(game)
                        except: continue
        except: pass

    # 2. Filtrar Afinidade
    afin_files = []
    for f in todos_arquivos:
        if f.endswith(".txt") and (
            "AfinidadeIA" in f or
            "AnaliseAfinidadeAtrasado" in f or
            "Afinidade_Clusters_" in f or 
            "Afinidade_IA_Duelo" in f
        ):
            afin_files.append(os.path.join(save_dir, f))
    
    latest_afin_game = []
    latest_a = None
    if afin_files:
        latest_a = max(afin_files, key=os.path.getmtime)
        try:
            with open(latest_a, 'r') as f_read:
                for line in f_read:
                    parts = line.strip().split()
                    if len(parts) >= 7:
                        try:
                            game = [int(x) for x in parts[:7]]
                            latest_afin_game.append(game)
                        except: continue
        except: pass

    return jsonify({
        'sucesso': True,
        'sniper': latest_sniper_game,
        'afinidade': latest_afin_game,
        'arquivo_sniper': os.path.basename(latest_s) if latest_s else None,
        'arquivo_afinidade': os.path.basename(latest_a) if latest_a else None
    })

@analise_atrasados_bp.route('/api/analise/comparativo/enviar-conferencia', methods=['POST'])
def enviar_duelo_conferencia():
    import os, glob
    from services.conferencia_historica_service import ConferenciaHistoricaService
    from flask import current_app
    
    data = request.json
    nome_sniper = data.get('arquivo_sniper')
    nome_afinidade = data.get('arquivo_afinidade')
    
    afin_dir = os.path.join(os.getcwd(), 'conferencia_filtros-baixados')
    mensagens = []
    
    # Processar Sniper
    if nome_sniper:
        path_s = os.path.join(afin_dir, nome_sniper)
        if os.path.exists(path_s):
            with open(path_s, 'r') as f: content = f.read()
            sessao_s = ConferenciaHistoricaService.criar_sessao(
                nome_arquivo=nome_sniper,
                descricao=f"Duelo: Sniper ({nome_sniper})",
                estrategia='ordenada', filtro_min=4
            )
            ConferenciaHistoricaService.processar_arquivo(sessao_s.id, content)
            mensagens.append(f"Sniper enviado (ID: {sessao_s.id})")

    # Processar Afinidade
    if nome_afinidade:
        path_a = os.path.join(afin_dir, nome_afinidade)
        if os.path.exists(path_a):
            with open(path_a, 'r') as f: content = f.read()
            sessao_a = ConferenciaHistoricaService.criar_sessao(
                nome_arquivo=nome_afinidade,
                descricao=f"Duelo: Afinidade ({nome_afinidade})",
                estrategia='ordenada', filtro_min=4
            )
            ConferenciaHistoricaService.processar_arquivo(sessao_a.id, content)
            mensagens.append(f"Afinidade enviada (ID: {sessao_a.id})")

    return jsonify({
        'sucesso': True,
        'mensagem': " | ".join(mensagens) if mensagens else "Nenhum arquivo enviado."
    })