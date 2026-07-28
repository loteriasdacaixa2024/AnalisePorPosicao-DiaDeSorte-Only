from models.shared import db
from models.sorteio import Sorteio
from sqlalchemy import text
import collections
import itertools

class AnaliseAfinidadeService:
    @staticmethod
    def obter_clusters_e_hubs(janela=30, força_minima=3):
        """
        Calcula a coocorrência de dezenas e identifica clusters e hubs.
        janela: número de concursos recentes (0 = todos)
        força_minima: número mínimo de vezes que um par deve sair junto para ser considerado link
        """
        query = Sorteio.query.order_by(Sorteio.concurso.desc())
        if janela > 0:
            query = query.limit(janela)
        
        sorteios = query.all()
        if not sorteios:
            return {"erro": "Nenhum sorteio encontrado para análise."}

        # Extrair dezenas de cada sorteio
        jogos = []
        for s in sorteios:
            dezenas = sorted([s.posicao_1, s.posicao_2, s.posicao_3, s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7])
            jogos.append(dezenas)

        # Contar coocorrência de pares
        pares_count = collections.Counter()
        for jogo in jogos:
            for par in itertools.combinations(jogo, 2):
                pares_count[par] += 1

        # Identificar Links Fortes (Afinidade)
        links = []
        conexoes_por_numero = collections.defaultdict(int)
        
        for (n1, n2), freq in pares_count.items():
            if freq >= força_minima:
                links.append({
                    "n1": n1,
                    "n2": n2,
                    "frequencia": freq
                })
                conexoes_por_numero[n1] += 1
                conexoes_por_numero[n2] += 1

        # Identificar Hubs (Números com mais conexões)
        hubs = sorted(
            [{"numero": n, "conexoes": c} for n, c in conexoes_por_numero.items()],
            key=lambda x: x["conexoes"],
            reverse=True
        )[:5]

        # Identificar Clusters (Grupos de 3 ou mais que se conectam muito)
        # Simplificação: Grupos de 3 (Triângulos)
        trios = collections.Counter()
        for jogo in jogos:
            for trio in itertools.combinations(jogo, 3):
                # Verificar se todos os pares do trio são fortes
                p1 = tuple(sorted((trio[0], trio[1])))
                p2 = tuple(sorted((trio[0], trio[2])))
                p3 = tuple(sorted((trio[1], trio[2])))
                
                if pares_count[p1] >= força_minima and \
                   pares_count[p2] >= força_minima and \
                   pares_count[p3] >= força_minima:
                    trios[tuple(sorted(trio))] += 1

        clusters = sorted(
            [{"dezenas": list(t), "frequencia": f} for t, f in trios.items()],
            key=lambda x: x["frequencia"],
            reverse=True
        )[:8]

        return {
            "janela": janela,
            "total_concursos": len(jogos),
            "hubs": hubs,
            "clusters": clusters,
            "links_detalhados": sorted(links, key=lambda x: x["frequencia"], reverse=True)[:20]
        }

    @staticmethod
    def gerar_apostas_afinidade(top_atrasados_list, janela=30, força_minima=2, qtd_apostas=50, 
                                excluir_numeros=None, dezenas_ciclo=None,
                                soma_min=80, soma_max=135, digitos_min=5, digitos_max=8, max_seq=3):
        """
        Gera apostas 'casando' dezenas atrasadas com afinidade e fechamento de CICLO.
        """
        if excluir_numeros is None: excluir_numeros = []
        if dezenas_ciclo is None: dezenas_ciclo = []
            
        params = AnaliseAfinidadeService.obter_clusters_e_hubs(janela=janela, força_minima=força_minima)
        if "erro" in params:
            return params

        # Filtros de segurança e Ciclo
        top_filtrado = [n for n in top_atrasados_list if n not in excluir_numeros]
        hubs_filtrados = [h["numero"] for h in params["hubs"] if h["numero"] not in excluir_numeros]
        ciclo_limpo = [n for n in dezenas_ciclo if n not in excluir_numeros]
        
        # Mapear afinidade
        afinidade = collections.defaultdict(list)
        for link in params.get("links_detalhados", []):
            if link["n1"] not in excluir_numeros and link["n2"] not in excluir_numeros:
                afinidade[link["n1"]].append(link["n2"])
                afinidade[link["n2"]].append(link["n1"])

        def is_valid_bet(game):
            soma = sum(game)
            if soma < soma_min or soma > soma_max: return False
            digits = set()
            for n in game:
                digits.add(n // 10)
                digits.add(n % 10)
            if len(digits) < digitos_min or len(digits) > digitos_max: return False
            
            # Filtro anti-sequencia dinâmico
            s_game = sorted(list(game))
            for idx in range(len(s_game) - max_seq):
                if s_game[idx+max_seq] - s_game[idx] == max_seq: return False
            return True

        valid_games = set()

        # ESTRATÉGIA A: FCO (Foco no Ciclo) + Clusters
        # Se existem dezenas pendentes no ciclo, elas são a BASE de tudo.
        base_ciclo = set(ciclo_limpo[:4]) # Pega até 4 dezenas do ciclo para não engessar o jogo
        
        if base_ciclo:
            for cl in params.get("clusters", []):
                cluster_base = set([d for d in cl["dezenas"] if d not in excluir_numeros])
                jogo_base = base_ciclo | cluster_base
                jogo_base = set(list(jogo_base)[:6]) # Garante espaço para completar
                
                possiveis = hubs_filtrados + [n for n in top_filtrado if n not in jogo_base]
                for extra in itertools.combinations(possiveis, 7 - len(jogo_base)):
                    game = tuple(sorted(list(jogo_base | set(extra))))
                    if len(set(game)) == 7 and is_valid_bet(game):
                        valid_games.add(game)
                    if len(valid_games) >= qtd_apostas: break
                if len(valid_games) >= qtd_apostas: break

        # ESTRATÉGIA B: Afinidade + Pendentes do Ciclo (Rotação)
        if len(valid_games) < qtd_apostas:
            for base_num in top_filtrado:
                parceiros = [p for p in afinidade.get(base_num, []) if p not in excluir_numeros]
                for p in (parceiros or [None]):
                    jogo_base = {base_num}
                    if p: jogo_base.add(p)
                    
                    # Adiciona pelo menos 2 dezenas do ciclo por jogo se existirem
                    for c_num in ciclo_limpo:
                        if len(jogo_base) < 4: jogo_base.add(c_num)
                    
                    restantes = [h for h in hubs_filtrados if h not in jogo_base] + \
                                [n for n in top_filtrado if n not in jogo_base]
                    
                    for extra in itertools.combinations(restantes, 7 - len(jogo_base)):
                        game = tuple(sorted(list(jogo_base | set(extra))))
                        if len(set(game)) == 7 and is_valid_bet(game):
                            valid_games.add(game)
                        if len(valid_games) >= qtd_apostas: break
                    if len(valid_games) >= qtd_apostas: break
                if len(valid_games) >= qtd_apostas: break

        return {
            "sucesso": True,
            "apostas": [list(g) for g in valid_games],
            "total": len(valid_games),
            "numeros_excluidos": excluir_numeros,
            "dezenas_ciclo_usadas": ciclo_limpo
        }
