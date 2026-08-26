from models.sorteio import Sorteio, db
from collections import defaultdict, Counter
import random
import math
from services.analise_numeros_juntos_service import AnaliseNumerosJuntosService
from services.posicao_minima_maxima_service import PosicaoMinimaMaximaService

class SistemaBlocosInteligenteService:
    
    @staticmethod
    def obter_estatisticas_base():
        """
        Calcula as estatísticas base para todos os 31 números
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
        if not sorteios:
            return None
            
        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso
        
        freqs = Counter()
        atrasos = {}
        # Inicializa atrasos com total_concursos (nunca saiu)
        for i in range(1, 32):
            atrasos[i] = total_concursos
            
        # Posições: freq_posicao[numero][posicao_1_to_7]
        freq_posicao = {i: Counter() for i in range(1, 32)}
        
        for s in sorteios:
            nums = s.get_posicoes_lista()
            for idx, n in enumerate(nums):
                freqs[n] += 1
                freq_posicao[n][idx+1] += 1
                if atrasos[n] == total_concursos: # Primeira vez que aparece vindo do topo (mais recente)
                    atrasos[n] = ultimo_concurso - s.concurso
        
        # Normalizar Frequências (0-1)
        max_freq = max(freqs.values()) if freqs else 1
        freq_norm = {i: freqs[i]/max_freq for i in range(1, 32)}
        
        # Normalizar Atrasos (0-1) - Quanto maior o atraso, maior o peso? 
        # Geralmente sim, pois "está devendo".
        max_atraso = max(atrasos.values()) if atrasos else 1
        atraso_norm = {i: atrasos[i]/max_atraso for i in range(1, 32)}
        
        # Posições: Probabilidade por posição
        prob_posicao = {i: {p: freq_posicao[i][p]/total_concursos for p in range(1, 8)} for i in range(1, 32)}
        
        # Correlação (usando AnaliseNumerosJuntosService)
        # Vamos pré-calcular um mapa de co-ocorrência simples
        correlacao_map = defaultdict(lambda: Counter())
        for s in sorteios:
            nums = s.get_posicoes_lista()
            for i in range(len(nums)):
                for j in range(i + 1, len(nums)):
                    n1, n2 = nums[i], nums[j]
                    correlacao_map[n1][n2] += 1
                    correlacao_map[n2][n1] += 1
        
        # Normalizar Correlação
        # Para cada n1, n2, corr = ocorrências_juntos / total_sorteios
        corr_norm = defaultdict(lambda: defaultdict(float))
        for n1, parceiros in correlacao_map.items():
            for n2, count in parceiros.items():
                # Normaliza pelo máximo de parcerias daquele número? 
                # Ou pelo total de concursos? Use total_concursos para ser absoluto.
                corr_norm[n1][n2] = count / total_concursos

        return {
            'ultimo_concurso': ultimo_concurso,
            'frequencia': freq_norm,
            'atraso': atraso_norm,
            'posicao': prob_posicao,
            'correlacao': corr_norm,
            'total_concursos': total_concursos,
            'ultimo_concurso_numeros': sorteios[0].get_posicoes_lista()
        }

    @staticmethod
    def gerar_jogos(config):
        """
        Gera jogos baseados na configuração inteligente com prioridade ao padrão.
        """
        stats = SistemaBlocosInteligenteService.obter_estatisticas_base()
        if not stats:
            return {'sucesso': False, 'mensagem': 'Erro ao obter estatísticas'}
            
        fixas = set(config.get('fixas', []))
        rotativas = set(config.get('rotativas', []))
        variaveis_u = set(config.get('variaveis', []))
        padroes = config.get('padroes', [])
        qtd_alvo = config.get('qtd_jogos', 10)
        dezenas_por_jogo = config.get('dezenas_por_jogo', 7)
        modo_bolao = config.get('modo_bolao', False)
        
        # Pool Preferencial (Números que o usuário marcou explicitamente)
        if not rotativas and not variaveis_u:
            # Se não marcou nada além das fixas, o preferencial é todo o resto
            pool_preferencial = {i for i in range(1, 32) if i not in fixas}
        else:
            pool_preferencial = (rotativas | variaveis_u) - fixas
            
        # Pool Absoluto (Todo o universo menos fixas) - usado para garantir o padrão
        pool_absoluto = {i for i in range(1, 32) if i not in fixas}
            
        jogos = []
        tentativas_total = 0
        
        while len(jogos) < qtd_alvo and tentativas_total < 5000:
            tentativas_total += 1
            
            # 1. Definir Padrão Alvo
            if padroes:
                padrao_str = random.choice(padroes)
                try:
                    target_groups_list = [int(x) for x in padrao_str.split()]
                    target_groups_counter = Counter(target_groups_list)
                except:
                    # Fallback se string vier mal formatada
                    target_groups_counter = None
            else:
                padrao_str = 'Aleatório'
                target_groups_counter = None
                
            # 2. Calcular o que falta do padrão após aplicar as fixas
            vagas_totais = dezenas_por_jogo - len(fixas)
            if vagas_totais < 0:
                continue # Jogo impossível (mais fixas que vagas)

            grupos_necessarios = [] # Lista de grupos que precisamos buscar
            
            if target_groups_counter:
                # Contar grupos das fixas
                fixas_groups = Counter([n // 10 for n in fixas])
                
                # Subtrair fixas do padrão
                # Ex: Padrão pede 3 G0. Fixas tem 2 G0. Falta 1 G0.
                # Ex: Padrão pede 1 G0. Fixas tem 2 G0. Falta -1 G0 (já atendido, ignora excesso).
                necessidade_real = target_groups_counter - fixas_groups
                
                # Transformar Counter em lista de grupos necessários
                for g, qtd in necessidade_real.items():
                    if qtd > 0:
                        grupos_necessarios.extend([g] * qtd)
                
                # Se precisarmos de mais números do que temos de vagas, temos que truncar.
                # Prioridade ao Padrão: Tentar atender o máximo possível.
                if len(grupos_necessarios) > vagas_totais:
                    # Embaralhar para não cortar sempre os últimos grupos (ex: G3)
                    random.shuffle(grupos_necessarios)
                    grupos_necessarios = grupos_necessarios[:vagas_totais]
                
                # Se sobrar vagas (padrão menor que dezenas do jogo?), preencher com 'Qualquer'
                # Isso é raro no Dia de Sorte (7 dezenas fixas no padrão), mas possível em bolão de 8+ dezenas
                while len(grupos_necessarios) < vagas_totais:
                    grupos_necessarios.append(None) # None = qualquer grupo
                    
            else:
                # Sem padrão, 3 vagas livres
                grupos_necessarios = [None] * vagas_totais
                
            # 3. Construir o Jogo
            jogo_atual = list(fixas)
            possivel = True
            
            # Para cada vaga necessária, buscar candidato
            # random.shuffle(grupos_necessarios) # Já embaralhado se truncado, mas bom garantir ordem não viciada
            
            for target_g in grupos_necessarios:
                cand_pool = []
                
                # Tentar encontrar candidato no Pool Preferencial
                candidatos_pref = [n for n in pool_preferencial if n not in jogo_atual]
                
                if target_g is not None:
                    # Filtrar pelo grupo
                    candidatos_validos = [n for n in candidatos_pref if (n // 10) == target_g]
                else:
                    candidatos_validos = candidatos_pref
                    
                # Se não achou no preferencial, buscar no Absoluto (PRIORIDADE AO PADRÃO)
                if not candidatos_validos:
                    candidatos_abs = [n for n in pool_absoluto if n not in jogo_atual]
                    if target_g is not None:
                        candidatos_validos = [n for n in candidatos_abs if (n // 10) == target_g]
                    else:
                        candidatos_validos = candidatos_abs
                
                if not candidatos_validos:
                    possivel = False
                    break
                    
                # Escolher o melhor candidato por score
                scores = []
                for n in candidatos_validos:
                    # Score Calculation
                    corr_sum = sum(stats['correlacao'][f][n] for f in fixas)
                    corr_factor = corr_sum / len(fixas) if fixas else 0
                    freq_factor = stats['frequencia'][n]
                    delay_factor = stats['atraso'][n]
                    
                    # Positional factor
                    temp_jogo = sorted(jogo_atual + [n])
                    pos_idx = temp_jogo.index(n) + 1
                    pos_factor = stats['posicao'][n].get(pos_idx, 0)
                    
                    total_score = (corr_factor * 0.35) + (freq_factor * 0.25) + (delay_factor * 0.20) + (pos_factor * 0.20)
                    scores.append((n, total_score))
                
                # Selecionar top ponderado
                scores.sort(key=lambda x: x[1], reverse=True)
                top_k = scores[:5] # Top 5
                if top_k:
                    escolhido = random.choice(top_k)[0]
                    jogo_atual.append(escolhido)
                else:
                    possivel = False
                    break
            
            if possivel:
                jogo_final = sorted(jogo_atual)
                # Validar unicidade
                if jogo_final not in [j['numeros'] for j in jogos]:
                    jogos.append({
                        'numeros': jogo_final,
                        'padrao': padrao_str if padroes else 'Aleatório',
                        'score_medio': 0
                    })
        
        return {
            'sucesso': True,
            'jogos': jogos,
            'concursos_base': stats['total_concursos'],
            'ultimo_concurso': stats['ultimo_concurso']
        }
