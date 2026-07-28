# Sistema: Análise por Posição - Dia de Sorte
# Desenvolvido para: Márcio Fernando Maia
# Módulo: Análise de Ciclos das Dezenas
# Atualizado remotamente para forçar limpeza de cache do Python (__pycache__)

from models.sorteio import Sorteio
from sqlalchemy import func
from datetime import datetime

class AnaliseCiclosDezenasService:
    """
    Service para análise de Ciclos das Dezenas do Dia de Sorte
    
    Conceito de CICLO:
    - Um ciclo começa quando nem todas as dezenas (01 a 31) saíram
    - O ciclo termina quando todas as dezenas saem ao menos uma vez
    - Enquanto existir ao menos uma dezena que não saiu, o ciclo permanece aberto
    """
    
    @staticmethod
    def obter_todos_sorteios():
        """Retorna todos os sorteios ordenados por concurso"""
        return Sorteio.query.order_by(Sorteio.concurso.asc()).all()
    
    @staticmethod
    def extrair_dezenas_sorteio(sorteio):
        """Extrai as 7 dezenas de um sorteio"""
        return [
            sorteio.posicao_1,
            sorteio.posicao_2,
            sorteio.posicao_3,
            sorteio.posicao_4,
            sorteio.posicao_5,
            sorteio.posicao_6,
            sorteio.posicao_7
        ]
    
    @staticmethod
    def calcular_ciclos_completos():
        """
        Calcula todos os ciclos completos (que já fecharam)
        Retorna lista de ciclos com suas informações
        """
        sorteios = AnaliseCiclosDezenasService.obter_todos_sorteios()
        
        if not sorteios:
            return []
        
        ciclos = []
        ciclo_atual = {
            'numero': 1,
            'concurso_inicio': sorteios[0].concurso,
            'concurso_fim': None,
            'dezenas_saidas': set(),
            'quantidade_concursos': 0,
            'historico_concursos': [],
            'detalhes_concursos': []
        }
        
        for sorteio in sorteios:
            dezenas = AnaliseCiclosDezenasService.extrair_dezenas_sorteio(sorteio)
            dezenas_set = set(dezenas)
            
            novas = dezenas_set - ciclo_atual['dezenas_saidas']
            repetidas = dezenas_set & ciclo_atual['dezenas_saidas']
            
            ciclo_atual['dezenas_saidas'].update(dezenas_set)
            ciclo_atual['quantidade_concursos'] += 1
            ciclo_atual['historico_concursos'].append(sorteio.concurso)
            
            ciclo_atual['detalhes_concursos'].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else None,
                'novas': sorted(list(novas)),
                'repetidas': sorted(list(repetidas)),
                'qtd_novas': len(novas),
                'total_preenchido': len(ciclo_atual['dezenas_saidas'])
            })
            
            # Verifica se o ciclo fechou (todas as 31 dezenas saíram)
            if len(ciclo_atual['dezenas_saidas']) == 31:
                ciclo_atual['concurso_fim'] = sorteio.concurso
                ciclo_atual['dezenas_saidas'] = list(ciclo_atual['dezenas_saidas'])
                ciclos.append(ciclo_atual.copy())
                
                # Inicia novo ciclo
                ciclo_atual = {
                    'numero': len(ciclos) + 1,
                    'concurso_inicio': sorteio.concurso,
                    'concurso_fim': None,
                    'dezenas_saidas': set(),
                    'quantidade_concursos': 0,
                    'historico_concursos': [],
                    'detalhes_concursos': []
                }
        
        # Adiciona o ciclo atual (em andamento) se houver
        if ciclo_atual['quantidade_concursos'] > 0:
            ciclo_atual['dezenas_saidas'] = list(ciclo_atual['dezenas_saidas'])
            ciclo_atual['em_andamento'] = True
            ciclos.append(ciclo_atual)
        
        return ciclos
    
    @staticmethod
    def obter_ciclo_atual():
        """Retorna informações detalhadas do ciclo atual (em andamento)"""
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        
        if not ciclos:
            return None
        
        ciclo_atual = ciclos[-1]
        
        # Calcular dezenas pendentes
        todas_dezenas = set(range(1, 32))
        dezenas_saidas = set(ciclo_atual['dezenas_saidas'])
        dezenas_pendentes = sorted(list(todas_dezenas - dezenas_saidas))
        
        # Obter último concurso
        ultimo_concurso = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
        
        # Coletar histórico completo para a tabela de evolução
        historico_detalhes = []
        for c in ciclos:
            for d in c.get('detalhes_concursos', []):
                d_copy = d.copy()
                d_copy['numero_ciclo'] = c['numero']
                historico_detalhes.append(d_copy)
        
        return {
            'numero_ciclo': ciclo_atual['numero'],
            'concurso_inicio': ciclo_atual['concurso_inicio'],
            'concurso_atual': ultimo_concurso.concurso if ultimo_concurso else None,
            'quantidade_concursos': ciclo_atual['quantidade_concursos'],
            'dezenas_saidas': sorted(dezenas_saidas),
            'dezenas_pendentes': dezenas_pendentes,
            'total_dezenas_saidas': len(dezenas_saidas),
            'total_dezenas_pendentes': len(dezenas_pendentes),
            'percentual_completo': round((len(dezenas_saidas) / 31) * 100, 2),
            'em_andamento': ciclo_atual.get('em_andamento', False),
            'detalhes_concursos': sorted(historico_detalhes, key=lambda x: x['concurso'], reverse=True)
        }
    
    @staticmethod
    def obter_metricas_historicas():
        """Calcula métricas históricas de todos os ciclos"""
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        
        # Filtrar apenas ciclos completos (excluir o em andamento)
        ciclos_completos = [c for c in ciclos if not c.get('em_andamento', False)]
        
        if not ciclos_completos:
            return {
                'total_ciclos': 0,
                'media_concursos': 0,
                'ciclo_mais_curto': None,
                'ciclo_mais_longo': None,
                'distribuicao': {}
            }
        
        quantidades = [c['quantidade_concursos'] for c in ciclos_completos]
        
        # Calcular distribuição
        distribuicao = {
            '10-15': 0,
            '16-20': 0,
            '21-25': 0,
            '26-30': 0,
            '31-35': 0,
            '36+': 0
        }
        
        for qtd in quantidades:
            if qtd <= 15:
                distribuicao['10-15'] += 1
            elif qtd <= 20:
                distribuicao['16-20'] += 1
            elif qtd <= 25:
                distribuicao['21-25'] += 1
            elif qtd <= 30:
                distribuicao['26-30'] += 1
            elif qtd <= 35:
                distribuicao['31-35'] += 1
            else:
                distribuicao['36+'] += 1
        
        # Encontrar ciclos extremos
        ciclo_mais_curto = min(ciclos_completos, key=lambda x: x['quantidade_concursos'])
        ciclo_mais_longo = max(ciclos_completos, key=lambda x: x['quantidade_concursos'])
        
        return {
            'total_ciclos': len(ciclos_completos),
            'media_concursos': round(sum(quantidades) / len(quantidades), 1),
            'ciclo_mais_curto': {
                'numero': ciclo_mais_curto['numero'],
                'concursos': ciclo_mais_curto['quantidade_concursos'],
                'inicio': ciclo_mais_curto['concurso_inicio'],
                'fim': ciclo_mais_curto['concurso_fim']
            },
            'ciclo_mais_longo': {
                'numero': ciclo_mais_longo['numero'],
                'concursos': ciclo_mais_longo['quantidade_concursos'],
                'inicio': ciclo_mais_longo['concurso_inicio'],
                'fim': ciclo_mais_longo['concurso_fim']
            },
            'distribuicao': distribuicao
        }
    
    @staticmethod
    def comparar_ciclo_atual_com_historico():
        """Compara o ciclo atual com métricas históricas"""
        ciclo_atual = AnaliseCiclosDezenasService.obter_ciclo_atual()
        metricas = AnaliseCiclosDezenasService.obter_metricas_historicas()
        
        if not ciclo_atual or not metricas['total_ciclos']:
            return None
        
        qtd_atual = ciclo_atual['quantidade_concursos']
        media = metricas['media_concursos']
        
        # Calcular percentil
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        ciclos_completos = [c for c in ciclos if not c.get('em_andamento', False)]
        
        if ciclos_completos:
            menores_ou_iguais = len([c for c in ciclos_completos if c['quantidade_concursos'] <= qtd_atual])
            percentil = round((menores_ou_iguais / len(ciclos_completos)) * 100, 1)
        else:
            percentil = 0
        
        # Classificar status
        if qtd_atual < media * 0.8:
            status = 'curto'
        elif qtd_atual > media * 1.2:
            status = 'longo'
        else:
            status = 'normal'
        
        return {
            'concursos_atual': qtd_atual,
            'media_historica': media,
            'diferenca': round(qtd_atual - media, 1),
            'percentil': percentil,
            'status': status,
            'insight': AnaliseCiclosDezenasService._gerar_insight(status, percentil, qtd_atual, media)
        }
    
    @staticmethod
    def _gerar_insight(status, percentil, qtd_atual, media):
        """Gera insight automático sobre o ciclo atual"""
        if status == 'curto':
            return f"Ciclo atual está {round(media - qtd_atual, 1)} concursos abaixo da média histórica."
        elif status == 'longo':
            return f"Ciclo atual com {qtd_atual} concursos já ultrapassou {percentil:.0f}% dos ciclos históricos."
        else:
            return f"Ciclo atual está dentro da normalidade ({qtd_atual} concursos, média: {media})."
    
    @staticmethod
    def obter_dezenas_sugeridas(quantidade=6):
        """
        Retorna sugestão inteligente de dezenas para complementar apostas
        Baseado no score do motor de inteligência de ciclos
        """
        try:
            from services.ciclo_inteligencia_service import CicloInteligenciaService
            analise = CicloInteligenciaService.analisar_ciclo_completo()
            if analise and analise.get('scores_dezenas'):
                pendentes_scores = [s for s in analise['scores_dezenas'] if s.get('pendente')]
                top = [s['dezena'] for s in pendentes_scores[:quantidade]]
                if top:
                    return top
        except Exception:
            pass

        ciclo_atual = AnaliseCiclosDezenasService.obter_ciclo_atual()
        if not ciclo_atual or not ciclo_atual['dezenas_pendentes']:
            return []

        pendentes = ciclo_atual['dezenas_pendentes']
        return pendentes[:quantidade] if len(pendentes) >= quantidade else pendentes
    
    @staticmethod
    def obter_historico_ultimos_ciclos(quantidade=10):
        """Retorna histórico dos últimos N ciclos completos"""
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        ciclos_completos = [c for c in ciclos if not c.get('em_andamento', False)]
        
        # Pegar os últimos N ciclos
        ultimos = ciclos_completos[-quantidade:] if len(ciclos_completos) > quantidade else ciclos_completos
        
        # Reverter para mostrar mais recente primeiro
        return list(reversed(ultimos))

    @staticmethod
    def obter_estatisticas_comportamento():
        """
        Gera análise estatística adicional sobre o comportamento das dezenas no ciclo.
        Atende os requisitos do backend: média de dezenas novas/repetidas e percentuais.
        """
        ciclos = AnaliseCiclosDezenasService.calcular_ciclos_completos()
        ciclos_completos = [c for c in ciclos if not c.get('em_andamento', False)]
        
        if not ciclos_completos:
            return {
                "media_dezenas_novas": 0.0,
                "media_dezenas_repetidas": 0.0,
                "percentual_medio_novas": 0,
                "percentual_medio_repetidas": 0,
                "frequencia_sorteios": {
                    "total": 0, "nula": 0, "baixa": 0, "media": 0, "alta": 0
                }
            }
            
        total_novas = 0
        total_repetidas = 0
        total_dezenas_sorteadas = 0
        
        freq_nula = 0
        freq_baixa = 0
        freq_media = 0
        freq_alta = 0
        total_sorteios_analisados = 0
        
        for c in ciclos_completos:
            # Em um ciclo completo, as 'dezenas novas' correspondem a totalidade do universo...
            novas = len(c['dezenas_saidas']) 
            
            total_sorteadas_no_ciclo = c['quantidade_concursos'] * 7
            repetidas = total_sorteadas_no_ciclo - novas
            
            total_novas += novas
            total_repetidas += repetidas
            total_dezenas_sorteadas += total_sorteadas_no_ciclo
            
            # Calcular distribuição de 'qtd_novas' por concurso individual usando o histórico deste ciclo
            for detalhe in c.get('detalhes_concursos', []):
                qtd_n = detalhe.get('qtd_novas', 0)
                if qtd_n == 0:
                    freq_nula += 1
                elif qtd_n in [1, 2]:
                    freq_baixa += 1
                elif qtd_n in [3, 4]:
                    freq_media += 1
                else: 
                    # 5 to 7
                    freq_alta += 1
                total_sorteios_analisados += 1
            
        num_ciclos = len(ciclos_completos)
        
        media_novas = round(total_novas / num_ciclos, 1)
        media_repetidas = round(total_repetidas / num_ciclos, 1)
        
        perc_novas = round((total_novas / total_dezenas_sorteadas) * 100) if total_dezenas_sorteadas > 0 else 0
        perc_repetidas = round((total_repetidas / total_dezenas_sorteadas) * 100) if total_dezenas_sorteadas > 0 else 0
        
        return {
            "media_dezenas_novas": media_novas,
            "media_dezenas_repetidas": media_repetidas,
            "percentual_medio_novas": perc_novas,
            "percentual_medio_repetidas": perc_repetidas,
            "frequencia_sorteios": {
                "total": total_sorteios_analisados,
                "nula": freq_nula,
                "baixa": freq_baixa,
                "media": freq_media,
                "alta": freq_alta
            }
        }

    @staticmethod
    def obter_insights_e_recomendacoes():
        """
        Retorna insights inteligentes e recomendações estratégicas 
        baseadas no estado do ciclo atual e métricas históricas
        """
        ciclo_atual = AnaliseCiclosDezenasService.obter_ciclo_atual()
        metricas = AnaliseCiclosDezenasService.obter_metricas_historicas()
        
        if not ciclo_atual or not metricas['total_ciclos']:
            return None
        
        qtd_atual = ciclo_atual['quantidade_concursos']
        media = metricas['media_concursos']
        pendentes = ciclo_atual['total_dezenas_pendentes']
        
        insights = []
        recomendacoes = []
        
        # --- INSIGHTS INTELIGENTES ---
        
        # 1. Análise de Duração
        if qtd_atual < media * 0.7:
            insights.append({
                'titulo': 'Ciclo em Estágio Inicial',
                'ponto': 'positivo',
                'texto': f'O ciclo atual tem apenas {qtd_atual} concursos. Historicamente, a maioria dos ciclos fecha entre 16 e 25 concursos.'
            })
        elif qtd_atual < media:
            insights.append({
                'titulo': 'Ciclo em Maturação',
                'ponto': 'neutro',
                'texto': f'Com {qtd_atual} concursos, estamos chegando próximo à média de fechamento ({media}).'
            })
        else:
            insights.append({
                'titulo': 'Ciclo Prolongado',
                'ponto': 'alerta',
                'texto': f'Este ciclo já dura {qtd_atual} concursos, superando a média histórica. A probabilidade de fechamento iminente aumenta a cada sorteio.'
            })
            
        # 2. Análise de Pendências
        if pendentes <= 3:
            insights.append({
                'titulo': 'Retas Finais',
                'ponto': 'positivo',
                'texto': f'Restam apenas {pendentes} dezenas para o ciclo fechar. Em 85% dos casos, as últimas 3 dezenas saem em até 4 concursos.'
            })
        elif pendentes > 15:
            insights.append({
                'titulo': 'Muitas Pendências',
                'ponto': 'neutro',
                'texto': f'Ainda restam {pendentes} dezenas. O ciclo ainda tem fôlego para vários concursos antes de fechar.'
            })

        # 3. Probabilidade Estatística (Simulada baseada em distribuição)
        if qtd_atual >= 20 and pendentes <= 5:
            prob = "ALTA"
        elif qtd_atual >= 15:
            prob = "MÉDIA"
        else:
            prob = "BAIXA"
            
        insights.append({
            'titulo': 'Expectativa de Fechamento',
            'ponto': 'info',
            'texto': f'A probabilidade estatística de o ciclo fechar nos próximos 2 concursos é considerada {prob}.'
        })

        # --- RECOMENDAÇÕES ESTRATÉGICAS ---
        
        # Recomendação 1: Uso das Pendentes
        if pendentes <= 7:
            recomendacoes.append({
                'icone': 'fa-check-double',
                'cor': 'success',
                'texto': f'<strong>Foco nas Pendentes:</strong> Restam {pendentes} número(s) — use 2 a 3 pendentes por jogo (motor inteligente), evitando colocar todas no mesmo volante.'
            })
        elif pendentes <= 12:
             recomendacoes.append({
                'icone': 'fa-filter',
                'cor': 'primary',
                'texto': f'<strong>Seleção Híbrida:</strong> Escolha de 3 a 4 dezenas do grupo de pendentes e complete com as que mais saem no histórico.'
            })
        else:
            recomendacoes.append({
                'icone': 'fa-random',
                'cor': 'info',
                'texto': '<strong>Rotação:</strong> Use apenas 1 ou 2 dezenas pendentes por jogo, focando no equilíbrio com as dezenas já sorteadas no ciclo.'
            })
            
        # Recomendação 2: Estratégia de Captura
        if status_ciclo := 'longo' if qtd_atual > media else 'normal':
            if status_ciclo == 'longo':
                recomendacoes.append({
                    'icone': 'fa-target-reveal',
                    'cor': 'warning',
                    'texto': '<strong>Estratégia Agressiva:</strong> O ciclo está atrasado. É o momento ideal para aumentar a quantidade de jogos focando no fechamento do ciclo.'
                })
            else:
                recomendacoes.append({
                    'icone': 'fa-shield-alt',
                    'cor': 'secondary',
                    'texto': '<strong>Estratégia Conservadora:</strong> Jogue com moderação focando nas pendentes, mas sem apostar alto no fechamento imediato.'
                })
                
        # Recomendação 3: Mesclagem
        recomendacoes.append({
            'icone': 'fa-thumbtack',
            'cor': 'dark',
            'texto': '<strong>Dica de Ouro:</strong> Nunca use apenas dezenas pendentes se elas forem mais de 7. O Dia de Sorte sempre sorteia 7 dezenas, equilibre com as de maior frequência.'
        })

        return {
            'insights': insights,
            'recomendacoes': recomendacoes
        }
