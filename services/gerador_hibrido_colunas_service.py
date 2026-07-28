import random
from itertools import combinations
from models.sorteio import Sorteio, db
from services.analise_ciclos_dezenas_service import AnaliseCiclosDezenasService
from services.analise_meses_service import AnaliseMesesService

class GeradorHibridoColunasService:
    """Serviço para a 11ª Aba - Estratégia Híbrida Estrutural por Colunas (Dia de Sorte)."""

    COLUMNS_MAP = {
        1: [1, 11, 21, 31],
        2: [2, 12, 22],
        3: [3, 13, 23],
        4: [4, 14, 24],
        5: [5, 15, 25],
        6: [6, 16, 26],
        7: [7, 17, 27],
        8: [8, 18, 28],
        9: [9, 19, 29],
        10: [10, 20, 30]
    }

    MONTHS_FULL = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    MONTHS_ABBR = {
        1: 'JAN', 2: 'FEV', 3: 'MAR', 4: 'ABR', 5: 'MAI', 6: 'JUN',
        7: 'JUL', 8: 'AGO', 9: 'SET', 10: 'OUT', 11: 'NOV', 12: 'DEZ'
    }

    @staticmethod
    def get_column_for_number(num):
        """Retorna a coluna de uma dezena (1 a 10)."""
        return num % 10 if num % 10 != 0 else 10

    @classmethod
    def get_hibrido_analise(cls):
        """Realiza análise estrutural pré-estratégia (histórico, ciclos, colunas e meses)."""
        try:
            # 1. Obter informações de ciclos do ciclo atual
            ciclo_atual = AnaliseCiclosDezenasService.obter_ciclo_atual()
            dezenas_pendentes = ciclo_atual['dezenas_pendentes'] if ciclo_atual else list(range(1, 32))
            
            # 2. Obter sorteios recentes e total de sorteios
            sorteios_recentes = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(100).all()
            all_sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
            
            total_concursos = len(all_sorteios)
            ultimo_concurso = all_sorteios[0].concurso if all_sorteios else 0
            
            if not all_sorteios:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum sorteio cadastrado no sistema.'
                }

            # 3. Mapear dezenas por coluna
            # E inicializar estatísticas das colunas
            colunas_stats = {}
            for col_idx in range(1, 11):
                colunas_stats[col_idx] = {
                    'coluna': col_idx,
                    'dezenas': cls.COLUMNS_MAP[col_idx],
                    'hits_recente': 0,
                    'hits_total': 0,
                    'atraso': 0,
                    'ultimo_concurso_sorteado': 0,
                    'pendentes_ciclo': [d for d in cls.COLUMNS_MAP[col_idx] if d in dezenas_pendentes],
                    'quente_fria_status': 'normal'
                }

            # Calcular atrasos e hits
            for col_idx in range(1, 11):
                dezenas_coluna = cls.COLUMNS_MAP[col_idx]
                
                # Atraso: número de concursos desde o último sorteio com alguma dezena da coluna
                encontrou_atraso = False
                atraso_count = 0
                for s in all_sorteios:
                    sorteio_dezenas = [
                        s.posicao_1, s.posicao_2, s.posicao_3,
                        s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7
                    ]
                    # Verifica interseção
                    if any(d in dezenas_coluna for d in sorteio_dezenas):
                        if not encontrou_atraso:
                            colunas_stats[col_idx]['atraso'] = atraso_count
                            colunas_stats[col_idx]['ultimo_concurso_sorteado'] = s.concurso
                            encontrou_atraso = True
                        colunas_stats[col_idx]['hits_total'] += 1
                    if not encontrou_atraso:
                        atraso_count += 1

                # Hits nos últimos 100
                for s in sorteios_recentes:
                    sorteio_dezenas = [
                        s.posicao_1, s.posicao_2, s.posicao_3,
                        s.posicao_4, s.posicao_5, s.posicao_6, s.posicao_7
                    ]
                    if any(d in dezenas_coluna for d in sorteio_dezenas):
                        colunas_stats[col_idx]['hits_recente'] += 1

            # Atribuir classificações e formatar
            colunas_lista = []
            for col_idx in range(1, 11):
                c_data = colunas_stats[col_idx]
                total_analisados_recente = min(total_concursos, 100)
                freq_recente_pct = (c_data['hits_recente'] / total_analisados_recente) * 100 if total_analisados_recente > 0 else 0
                freq_total_pct = (c_data['hits_total'] / total_concursos) * 100
                
                # Classificar status
                if freq_recente_pct >= 65:
                    status = 'quente'
                elif freq_recente_pct <= 35:
                    status = 'fria'
                elif c_data['atraso'] >= 3:
                    status = 'atrasada'
                else:
                    status = 'normal'
                
                c_data['frequencia_recente'] = round(freq_recente_pct, 2)
                c_data['frequencia_total'] = round(freq_total_pct, 2)
                c_data['quente_fria_status'] = status
                colunas_lista.append(c_data)

            # 4. Decisão automática (Recomendação)
            colunas_atrasadas = [c for c in colunas_lista if c['atraso'] >= 3]
            colunas_frias = [c for c in colunas_lista if c['quente_fria_status'] == 'fria']
            
            total_pendentes = len(dezenas_pendentes)
            
            if total_pendentes <= 4:
                modo_sugerido = 'hibrido'
                titulo_rec = 'Modo Híbrido Estrutural (Recomendado)'
                motivo = f"O ciclo atual está na reta final com apenas {total_pendentes} dezenas pendentes ({', '.join(f'{d:02d}' for d in dezenas_pendentes)}). O modo Híbrido permite focar no fechamento destas dezenas integrando análise vertical (colunas) e horizontal (linhas)."
            elif len(colunas_atrasadas) >= 3:
                modo_sugerido = 'coluna'
                titulo_rec = 'Estratégia de Colunas (Recomendado)'
                cols_str = ', '.join(f"Col {c['coluna']}" for c in colunas_atrasadas)
                motivo = f"Detectamos {len(colunas_atrasadas)} colunas com atraso crítico ({cols_str}). Focar em fechamento de colunas completas é a melhor opção para capturar dezenas nestes setores represados."
            elif len(colunas_frias) >= 4:
                modo_sugerido = 'hibrido'
                titulo_rec = 'Modo Híbrido com Foco em Frias (Recomendado)'
                cols_str = ', '.join(f"Col {c['coluna']}" for c in colunas_frias)
                motivo = f"Há muitas colunas inativas ou frias recentemente ({cols_str}). O modo Híbrido permitirá reaproveitar dezenas com fechamento parcial dessas colunas, minimizando o risco."
            else:
                modo_sugerido = 'hibrido'
                titulo_rec = 'Modo Híbrido Equilibrado (Recomendado)'
                motivo = "A distribuição recente de colunas e linhas está equilibrada. Recomendamos o modo Híbrido por oferecer o maior controle de cobertura, mesclando dezenas quentes e pendentes do ciclo."

            # 5. Mês da sorte análise
            stats_meses = AnaliseMesesService.obter_estatisticas_meses()
            meses_lista = stats_meses.get('meses', [])
            
            # Ordenado por atraso, o primeiro é o mais atrasado
            mes_mais_atrasado = meses_lista[0] if meses_lista else None
            # Encontrar o de maior frequência
            mes_mais_frequente = max(meses_lista, key=lambda x: x['frequencia']) if meses_lista else None
            
            recomendacao_mes = {
                'atrasado_num': mes_mais_atrasado['numero'] if mes_mais_atrasado else 1,
                'atrasado_nome': mes_mais_atrasado['nome'] if mes_mais_atrasado else 'Janeiro',
                'atrasado_concursos': mes_mais_atrasado['atraso'] if mes_mais_atrasado else 0,
                'frequente_num': mes_mais_frequente['numero'] if mes_mais_frequente else 1,
                'frequente_nome': mes_mais_frequente['nome'] if mes_mais_frequente else 'Janeiro',
                'frequente_aparicoes': mes_mais_frequente['frequencia'] if mes_mais_frequente else 0
            }

            return {
                'sucesso': True,
                'ultimo_concurso': ultimo_concurso,
                'ciclo_atual': {
                    'numero': ciclo_atual['numero_ciclo'] if ciclo_atual else 1,
                    'concursos_duracao': ciclo_atual['quantidade_concursos'] if ciclo_atual else 0,
                    'dezenas_pendentes': dezenas_pendentes,
                    'total_pendentes': total_pendentes
                },
                'colunas': colunas_lista,
                'recomendacao': {
                    'modo': modo_sugerido,
                    'titulo': titulo_rec,
                    'motivo': motivo
                },
                'recomendacao_mes': recomendacao_mes
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'sucesso': False,
                'mensagem': f"Erro ao realizar análise híbrida: {str(e)}"
            }

    @classmethod
    def gerar_apostas_hibrido(cls, quantidade, dezenas_por_jogo, modo, 
                               colunas_selecionadas=None, fechar_colunas_completas=None,
                               reaproveitar_restantes=True, cobertura_desejada='alta',
                               mes_selecionado='aleatorio', valor_aposta=2.50):
        """
        Algoritmo inteligente para geração de apostas híbridas estruturais por colunas.
        Suporta de 7 a 15 dezenas por jogo, controle de fechamento completo/parcial,
        reaproveitamento das restantes e cobertura progressiva.
        """
        try:
            # 1. Validar quantidade de dezenas
            if not (7 <= dezenas_por_jogo <= 15):
                return {
                    'sucesso': False,
                    'mensagem': 'A quantidade de dezenas por jogo deve ser entre 7 e 15.'
                }

            # 2. Obter análise prévia para context
            analise = cls.get_hibrido_analise()
            if not analise['sucesso']:
                return analise
            
            dezenas_pendentes = analise['ciclo_atual']['dezenas_pendentes']
            
            # 3. Tratar colunas selecionadas
            if not colunas_selecionadas:
                # Automático: Seleciona colunas baseadas em atraso e dezenas pendentes do ciclo
                # Pega as 5 colunas com maior atraso
                colunas_ordenadas = sorted(analise['colunas'], key=lambda x: (x['atraso'], len(x['pendentes_ciclo'])), reverse=True)
                colunas_selecionadas = [c['coluna'] for c in colunas_ordenadas[:5]]
            else:
                colunas_selecionadas = [int(c) for c in colunas_selecionadas]

            if not fechar_colunas_completas:
                fechar_colunas_completas = []
            else:
                fechar_colunas_completas = [int(c) for c in fechar_colunas_completas]

            # 4. Tratar Mês da Sorte
            if mes_selecionado == 'aleatorio':
                mes_num = random.randint(1, 12)
            elif mes_selecionado == 'atrasado':
                mes_num = analise['recomendacao_mes']['atrasado_num']
            elif mes_selecionado == 'frequente':
                mes_num = analise['recomendacao_mes']['frequente_num']
            else:
                mes_num = int(mes_selecionado)

            mes_nome = cls.MONTHS_FULL.get(mes_num, 'N/A')
            mes_abbr = cls.MONTHS_ABBR.get(mes_num, 'JAN')

            # 5. Construir pools de dezenas
            # A) Dezenas obrigatórias (fechamento completo das colunas especificadas)
            dezenas_obrigatorias = set()
            for col in fechar_colunas_completas:
                dezenas_obrigatorias.update(cls.COLUMNS_MAP[col])
            
            dezenas_obrigatorias = list(dezenas_obrigatorias)
            
            if len(dezenas_obrigatorias) > dezenas_por_jogo:
                return {
                    'sucesso': False,
                    'mensagem': f"As colunas fechadas completamente somam {len(dezenas_obrigatorias)} dezenas, o que ultrapassa o limite do jogo ({dezenas_por_jogo}). Por favor, selecione menos colunas para fechamento completo."
                }

            # B) Pool principal (dezenas pertencentes às colunas selecionadas)
            pool_selecionado = set()
            for col in colunas_selecionadas:
                pool_selecionado.update(cls.COLUMNS_MAP[col])
            
            # Remover dezenas obrigatórias do pool selecionado
            pool_selecionado = pool_selecionado - set(dezenas_obrigatorias)
            pool_selecionado = list(pool_selecionado)

            # C) Dezenas restantes (fora das colunas selecionadas)
            pool_restantes = set(range(1, 32)) - set(dezenas_obrigatorias) - set(pool_selecionado)
            pool_restantes = list(pool_restantes)

            # 6. Algoritmo de geração com Cobertura Progressiva e Reaproveitamento
            apostas = []
            assinaturas = set()
            
            # Para garantir "reaproveitamento inteligente das restantes" e "cobertura progressiva das 31 dezenas":
            # Vamos manter um contador de uso de cada dezena nas apostas geradas.
            dezenas_uso_count = {d: 0 for d in range(1, 32)}
            
            # Prioridade de pesos:
            # - Dezenas pendentes do ciclo que estão no pool selecionado devem ter peso altíssimo.
            # - Outras dezenas do pool selecionado têm peso alto.
            # - Dezenas pendentes do ciclo que estão fora do pool têm peso médio-alto.
            # - Outras dezenas têm peso baseado em frequência e uso recente (reaproveitamento de dezenas menos usadas para expandir cobertura).

            for jogo_idx in range(quantidade):
                aposta = dezenas_obrigatorias[:]
                
                # Criar lista de candidatos disponíveis para esta aposta
                candidatos_pool = pool_selecionado[:]
                candidatos_restantes = pool_restantes[:]
                
                # Peso e ordenação inteligente para maximizar cobertura:
                # Dezenas que foram MENOS usadas nas apostas anteriores ganham prioridade
                def calcular_prioridade(d):
                    # Fator de uso (quanto menos usada, maior a prioridade)
                    uso_fator = 100 - (dezenas_uso_count[d] * 15)
                    # Bônus se for dezena pendente de ciclo
                    ciclo_bonus = 40 if d in dezenas_pendentes else 0
                    # Bônus se estiver no pool selecionado
                    pool_bonus = 30 if d in pool_selecionado else 0
                    return max(1, uso_fator + ciclo_bonus + pool_bonus)

                # Loop para preencher a aposta
                tentativa = 0
                max_tentativas_jogo = 100
                
                while len(aposta) < dezenas_por_jogo and tentativa < max_tentativas_jogo:
                    tentativa += 1
                    
                    # Decidir de qual pool tirar a dezena
                    # Se o modo é 'coluna', tentamos usar prioritariamente candidatos do pool_selecionado.
                    # Se 'hibrido', misturamos.
                    # Se a cobertura desejada for 'alta' ou se 'reaproveitar_restantes' for ativo, 
                    # e já tivermos colocado dezenas do pool principal, incluímos dezenas restantes.
                    
                    usa_restante = False
                    if modo == 'linha':
                        # Linha pura ou mais horizontalizada: dá pesos iguais aos números de acordo com a linha, mas aqui simulamos misturando
                        usa_restante = random.random() < 0.4
                    elif modo == 'hibrido':
                        # Híbrido: mescla
                        if len(aposta) >= (dezenas_por_jogo // 2) and reaproveitar_restantes:
                            usa_restante = random.random() < 0.5
                        else:
                            usa_restante = random.random() < 0.2
                    else:
                        # Colunas: foca nas colunas selecionadas
                        if not candidatos_pool:
                            usa_restante = True
                    
                    if usa_restante and candidatos_restantes:
                        # Sortear com peso baseado no uso histórico de dezenas para cobrir mais números
                        pesos = [calcular_prioridade(d) for d in candidatos_restantes]
                        escolhido = random.choices(candidatos_restantes, weights=pesos, k=1)[0]
                        candidatos_restantes.remove(escolhido)
                    elif candidatos_pool:
                        pesos = [calcular_prioridade(d) for d in candidatos_pool]
                        escolhido = random.choices(candidatos_pool, weights=pesos, k=1)[0]
                        candidatos_pool.remove(escolhido)
                    elif candidatos_restantes:
                        pesos = [calcular_prioridade(d) for d in candidatos_restantes]
                        escolhido = random.choices(candidatos_restantes, weights=pesos, k=1)[0]
                        candidatos_restantes.remove(escolhido)
                    else:
                        break # Sem mais números disponíveis
                        
                    if escolhido not in aposta:
                        aposta.append(escolhido)
                
                # Se completou a aposta e é inédita, salva
                aposta_ordenada = sorted(aposta)
                assinatura = '-'.join(map(str, aposta_ordenada))
                
                if len(aposta_ordenada) == dezenas_por_jogo and assinatura not in assinaturas:
                    assinaturas.add(assinatura)
                    apostas.append(aposta_ordenada)
                    # Atualizar contador de uso
                    for d in aposta_ordenada:
                        dezenas_uso_count[d] += 1
                else:
                    # Tentar gerar novamente
                    # Para não entrar em loop infinito
                    if len(assinaturas) >= (jogo_idx + 1):
                        continue

            # Caso não tenha conseguido gerar tudo
            if len(apostas) < quantidade:
                # Fallback: se houver poucas combinações inéditas possíveis, relaxar duplicidade
                # Mas no Dia de Sorte, 7 a 15 dezenas geram milhões de opções, então é raro falhar
                pass

            # 7. Métricas de Cobertura Progressiva
            dezenas_unicas = set()
            for ap in apostas:
                dezenas_unicas.update(ap)
            
            percentual_cobertura = round((len(dezenas_unicas) / 31) * 100, 2)
            dezenas_faltantes = sorted(list(set(range(1, 32)) - dezenas_unicas))
            dezenas_utilizadas = sorted(list(dezenas_unicas))
            
            # Colunas completas vs parciais vs vazias nas apostas
            colunas_completas_geradas = []
            colunas_parciais_geradas = []
            colunas_vazias_geradas = []
            
            for col_idx in range(1, 11):
                dezenas_col = cls.COLUMNS_MAP[col_idx]
                inclusas = [d for d in dezenas_col if d in dezenas_unicas]
                
                if len(inclusas) == len(dezenas_col):
                    colunas_completas_geradas.append(col_idx)
                elif len(inclusas) > 0:
                    colunas_parciais_geradas.append({
                        'coluna': col_idx,
                        'total_inclusas': len(inclusas),
                        'inclusas': inclusas,
                        'faltantes': sorted(list(set(dezenas_col) - set(inclusas)))
                    })
                else:
                    colunas_vazias_geradas.append(col_idx)

            # Dezenas pendentes de ciclo que foram cobertas
            pendentes_ciclo_cobertas = sorted([d for d in dezenas_pendentes if d in dezenas_unicas])
            pendentes_ciclo_faltantes = sorted([d for d in dezenas_pendentes if d not in dezenas_unicas])

            return {
                'sucesso': True,
                'apostas': apostas,
                'quantidade': len(apostas),
                'mes': mes_nome,
                'mes_num': mes_num,
                'mes_abbr': mes_abbr,
                'valor_unitario': valor_aposta,
                'valor_total': len(apostas) * valor_aposta,
                'modo': modo,
                'estrategias': {
                    'modo': modo,
                    'colunas_selecionadas': colunas_selecionadas,
                    'fechar_colunas_completas': fechar_colunas_completas,
                    'reaproveitar_restantes': reaproveitar_restantes,
                    'cobertura_desejada': cobertura_desejada
                },
                'cobertura': {
                    'percentual': percentual_cobertura,
                    'dezenas_utilizadas': dezenas_utilizadas,
                    'dezenas_faltantes': dezenas_faltantes,
                    'total_utilizadas': len(dezenas_utilizadas),
                    'total_faltantes': len(dezenas_faltantes),
                    'colunas_completas': colunas_completas_geradas,
                    'colunas_parciais': colunas_parciais_geradas,
                    'colunas_vazias': colunas_vazias_geradas,
                    'ciclo_pendentes_cobertas': pendentes_ciclo_cobertas,
                    'ciclo_pendentes_faltantes': pendentes_ciclo_faltantes,
                    'total_ciclo_cobertas': len(pendentes_ciclo_cobertas),
                    'total_ciclo_faltantes': len(pendentes_ciclo_faltantes)
                }
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'sucesso': False,
                'mensagem': f"Erro ao gerar apostas híbridas: {str(e)}"
            }
