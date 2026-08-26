# Sistema: Análise por Posição - Dia de Sorte
# Módulo: posicao_por_repeticao
# Desenvolvido para: Márcio Fernando Maia

from models.sorteio import Sorteio, db
from sqlalchemy import func
from collections import Counter, defaultdict

class RepeticaoService:
    """
    Serviço de análise de repetição de números por posição.
    Analisa a tendência histórica de 1-2 números se repetirem
    do concurso anterior para o seguinte.
    """

    # Nomes dos meses
    MESES_NOMES = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março',
        4: 'Abril', 5: 'Maio', 6: 'Junho',
        7: 'Julho', 8: 'Agosto', 9: 'Setembro',
        10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }

    @staticmethod
    def analisar_repeticoes_completo():
        """
        Análise completa de repetições entre concursos consecutivos.
        Retorna ranking, insights e recomendações.
        """
        try:
            # Buscar todos os sorteios ordenados por concurso
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if len(sorteios) < 2:
                return {'erro': 'Dados insuficientes para análise de repetição'}

            total_comparacoes = len(sorteios) - 1

            # Contadores por posição de ORIGEM (onde o número estava no concurso anterior)
            repeticoes_por_posicao_origem = defaultdict(int)

            # Contadores por posição de DESTINO (onde o número apareceu no concurso seguinte)
            repeticoes_por_posicao_destino = defaultdict(int)

            # Contador de quantas repetições por concurso
            repeticoes_por_concurso = []

            # Análise por mês
            repeticoes_por_mes = defaultdict(lambda: {'total': 0, 'com_repeticao': 0, 'repeticoes': 0})

            # Detalhes das repetições recentes (últimos 20)
            repeticoes_recentes = []

            # Matriz de transição (origem -> destino)
            matriz_transicao = defaultdict(lambda: defaultdict(int))

            # Analisar cada par de concursos consecutivos
            for i in range(1, len(sorteios)):
                anterior = sorteios[i - 1]
                atual = sorteios[i]

                # Números do concurso anterior (por posição)
                numeros_anterior = {
                    1: anterior.posicao_1,
                    2: anterior.posicao_2,
                    3: anterior.posicao_3,
                    4: anterior.posicao_4,
                    5: anterior.posicao_5,
                    6: anterior.posicao_6,
                    7: anterior.posicao_7
                }

                # Números do concurso atual (por posição)
                numeros_atual = {
                    1: atual.posicao_1,
                    2: atual.posicao_2,
                    3: atual.posicao_3,
                    4: atual.posicao_4,
                    5: atual.posicao_5,
                    6: atual.posicao_6,
                    7: atual.posicao_7
                }

                # Conjunto de números do concurso anterior
                set_anterior = set(numeros_anterior.values())

                # Verificar repetições
                qtd_repeticoes = 0
                detalhes_repeticao = []

                for pos_atual, num_atual in numeros_atual.items():
                    if num_atual in set_anterior:
                        qtd_repeticoes += 1

                        # Encontrar a posição de origem
                        pos_origem = None
                        for pos_ant, num_ant in numeros_anterior.items():
                            if num_ant == num_atual:
                                pos_origem = pos_ant
                                break

                        if pos_origem:
                            repeticoes_por_posicao_origem[pos_origem] += 1
                            repeticoes_por_posicao_destino[pos_atual] += 1
                            matriz_transicao[pos_origem][pos_atual] += 1

                            detalhes_repeticao.append({
                                'numero': num_atual,
                                'posicao_origem': pos_origem,
                                'posicao_destino': pos_atual,
                                'mesma_posicao': pos_origem == pos_atual
                            })

                repeticoes_por_concurso.append(qtd_repeticoes)

                # Análise por mês
                mes = atual.mes_sorte
                if mes:
                    repeticoes_por_mes[mes]['total'] += 1
                    if qtd_repeticoes > 0:
                        repeticoes_por_mes[mes]['com_repeticao'] += 1
                    repeticoes_por_mes[mes]['repeticoes'] += qtd_repeticoes

                # Guardar detalhes recentes (últimos 20)
                if i >= len(sorteios) - 20:
                    repeticoes_recentes.append({
                        'concurso_anterior': anterior.concurso,
                        'concurso_atual': atual.concurso,
                        'qtd_repeticoes': qtd_repeticoes,
                        'detalhes': detalhes_repeticao
                    })

            # ========================================
            # RANKING POR POSIÇÃO DE ORIGEM
            # ========================================
            ranking_origem = []
            for pos in range(1, 8):
                total = repeticoes_por_posicao_origem[pos]
                percentual = round((total / total_comparacoes) * 100, 2) if total_comparacoes > 0 else 0
                ranking_origem.append({
                    'posicao': pos,
                    'total_repeticoes': total,
                    'percentual': percentual,
                    'classificacao': RepeticaoService._classificar_posicao(percentual)
                })

            ranking_origem.sort(key=lambda x: x['total_repeticoes'], reverse=True)

            # ========================================
            # RANKING POR POSIÇÃO DE DESTINO
            # ========================================
            ranking_destino = []
            for pos in range(1, 8):
                total = repeticoes_por_posicao_destino[pos]
                percentual = round((total / total_comparacoes) * 100, 2) if total_comparacoes > 0 else 0
                ranking_destino.append({
                    'posicao': pos,
                    'total_repeticoes': total,
                    'percentual': percentual,
                    'classificacao': RepeticaoService._classificar_posicao(percentual)
                })

            ranking_destino.sort(key=lambda x: x['total_repeticoes'], reverse=True)

            # ========================================
            # ESTATÍSTICAS DE REPETIÇÃO POR CONCURSO
            # ========================================
            distribuicao_repeticoes = Counter(repeticoes_por_concurso)

            estatisticas_repeticao = {
                'total_comparacoes': total_comparacoes,
                'media_repeticoes': round(sum(repeticoes_por_concurso) / len(repeticoes_por_concurso), 2),
                'concursos_sem_repeticao': distribuicao_repeticoes.get(0, 0),
                'concursos_com_1_repeticao': distribuicao_repeticoes.get(1, 0),
                'concursos_com_2_repeticoes': distribuicao_repeticoes.get(2, 0),
                'concursos_com_3_ou_mais': sum(v for k, v in distribuicao_repeticoes.items() if k >= 3),
                'percentual_com_repeticao': round(
                    ((total_comparacoes - distribuicao_repeticoes.get(0, 0)) / total_comparacoes) * 100, 2
                ) if total_comparacoes > 0 else 0
            }

            # ========================================
            # ANÁLISE POR MÊS DA SORTE
            # ========================================
            analise_meses = []
            for mes, dados in repeticoes_por_mes.items():
                if dados['total'] > 0:
                    taxa = round((dados['com_repeticao'] / dados['total']) * 100, 2)
                    media = round(dados['repeticoes'] / dados['total'], 2)
                    analise_meses.append({
                        'mes': mes,
                        'nome': RepeticaoService.MESES_NOMES.get(mes, str(mes)),
                        'total_concursos': dados['total'],
                        'com_repeticao': dados['com_repeticao'],
                        'taxa_repeticao': taxa,
                        'media_repeticoes': media
                    })

            analise_meses.sort(key=lambda x: x['taxa_repeticao'], reverse=True)

            # ========================================
            # INSIGHTS INTELIGENTES
            # ========================================
            insights = RepeticaoService._gerar_insights(
                ranking_origem, ranking_destino, estatisticas_repeticao, analise_meses
            )

            # ========================================
            # RECOMENDAÇÕES ESTRATÉGICAS
            # ========================================
            recomendacoes = RepeticaoService._gerar_recomendacoes(
                ranking_origem, ranking_destino, estatisticas_repeticao
            )

            # ========================================
            # MATRIZ DE TRANSIÇÃO (Top 5)
            # ========================================
            top_transicoes = []
            for origem, destinos in matriz_transicao.items():
                for destino, qtd in destinos.items():
                    top_transicoes.append({
                        'origem': origem,
                        'destino': destino,
                        'quantidade': qtd,
                        'percentual': round((qtd / total_comparacoes) * 100, 2)
                    })

            top_transicoes.sort(key=lambda x: x['quantidade'], reverse=True)
            top_transicoes = top_transicoes[:10]

            return {
                'ranking_origem': ranking_origem,
                'ranking_destino': ranking_destino,
                'estatisticas': estatisticas_repeticao,
                'analise_meses': analise_meses,
                'insights': insights,
                'recomendacoes': recomendacoes,
                'top_transicoes': top_transicoes,
                'repeticoes_recentes': repeticoes_recentes[-10:]  # Últimas 10
            }

        except Exception as e:
            print(f"❌ Erro na análise de repetição: {str(e)}")
            return {'erro': str(e)}

    @staticmethod
    def _classificar_posicao(percentual):
        """Classifica a posição com base no percentual de repetição"""
        if percentual >= 20:
            return 'quente'
        elif percentual >= 12:
            return 'morna'
        elif percentual >= 8:
            return 'neutra'
        else:
            return 'fria'

    @staticmethod
    def _gerar_insights(ranking_origem, ranking_destino, estatisticas, analise_meses):
        """Gera insights inteligentes baseados na análise"""
        insights = []

        # Insight 1: Taxa geral de repetição
        taxa = estatisticas['percentual_com_repeticao']
        if taxa >= 70:
            insights.append({
                'tipo': 'destaque',
                'icone': 'fas fa-fire',
                'titulo': 'Alta Taxa de Repetição',
                'texto': f'Em {taxa}% dos concursos, pelo menos 1 número se repete do anterior!'
            })
        else:
            insights.append({
                'tipo': 'info',
                'icone': 'fas fa-chart-line',
                'titulo': 'Taxa de Repetição',
                'texto': f'{taxa}% dos concursos têm pelo menos 1 número repetido.'
            })

        # Insight 2: Posição de origem mais quente
        if ranking_origem:
            top = ranking_origem[0]
            insights.append({
                'tipo': 'quente',
                'icone': 'fas fa-bullseye',
                'titulo': f'Posição {top["posicao"]} é a Campeã de Origem',
                'texto': f'Números na P{top["posicao"]} se repetem em {top["percentual"]}% das vezes. Fique de olho!'
            })

        # Insight 3: Posição de destino mais quente
        if ranking_destino:
            top_dest = ranking_destino[0]
            insights.append({
                'tipo': 'quente',
                'icone': 'fas fa-crosshairs',
                'titulo': f'Posição {top_dest["posicao"]} Recebe Mais Repetições',
                'texto': f'Números repetidos aparecem mais na P{top_dest["posicao"]} ({top_dest["percentual"]}%).'
            })

        # Insight 4: Posição fria (menos repete)
        if ranking_origem:
            fria = ranking_origem[-1]
            if fria['percentual'] < 10:
                insights.append({
                    'tipo': 'frio',
                    'icone': 'fas fa-snowflake',
                    'titulo': f'Posição {fria["posicao"]} é Zona Fria',
                    'texto': f'Números na P{fria["posicao"]} raramente se repetem ({fria["percentual"]}%). Ideal para variação.'
                })

        # Insight 5: Média de repetições
        media = estatisticas['media_repeticoes']
        insights.append({
            'tipo': 'info',
            'icone': 'fas fa-calculator',
            'titulo': 'Média de Repetições',
            'texto': f'Em média, {media} número(s) se repete(m) por concurso.'
        })

        # Insight 6: Mês com mais repetição
        if analise_meses:
            mes_top = analise_meses[0]
            insights.append({
                'tipo': 'mes',
                'icone': 'fas fa-calendar-alt',
                'titulo': f'{mes_top["nome"]} Favorece Repetições',
                'texto': f'Quando o mês da sorte é {mes_top["nome"]}, {mes_top["taxa_repeticao"]}% têm repetição.'
            })

        return insights

    @staticmethod
    def _gerar_recomendacoes(ranking_origem, ranking_destino, estatisticas):
        """Gera recomendações estratégicas para o gerador de palpites"""
        recomendacoes = []

        # Top 3 posições de origem
        top3_origem = [r['posicao'] for r in ranking_origem[:3]]

        # Top 3 posições de destino
        top3_destino = [r['posicao'] for r in ranking_destino[:3]]

        # Recomendação 1: Fixação de números
        recomendacoes.append({
            'tipo': 'conservador',
            'icone': 'fas fa-lock',
            'titulo': 'Estratégia Conservadora',
            'texto': f'Considere manter 1-2 números das posições P{top3_origem[0]} e P{top3_origem[1]} do último concurso.',
            'posicoes': top3_origem[:2]
        })

        # Recomendação 2: Onde colocar repetições
        recomendacoes.append({
            'tipo': 'destino',
            'icone': 'fas fa-map-marker-alt',
            'titulo': 'Posições Receptoras',
            'texto': f'Números repetidos aparecem mais nas posições P{top3_destino[0]}, P{top3_destino[1]} e P{top3_destino[2]}.',
            'posicoes': top3_destino
        })

        # Recomendação 3: Variação
        frias = [r['posicao'] for r in ranking_origem if r['classificacao'] == 'fria']
        if frias:
            recomendacoes.append({
                'tipo': 'agressivo',
                'icone': 'fas fa-random',
                'titulo': 'Estratégia de Variação',
                'texto': f'Para apostas mais agressivas, varie os números nas posições {", ".join([f"P{p}" for p in frias])}.',
                'posicoes': frias
            })

        # Recomendação 4: Quantos repetir
        if estatisticas['concursos_com_1_repeticao'] > estatisticas['concursos_com_2_repeticoes']:
            recomendacoes.append({
                'tipo': 'quantidade',
                'icone': 'fas fa-dice-one',
                'titulo': 'Quantidade Ideal',
                'texto': 'O padrão mais comum é repetir apenas 1 número. Não exagere nas repetições!',
                'posicoes': []
            })
        else:
            recomendacoes.append({
                'tipo': 'quantidade',
                'icone': 'fas fa-dice-two',
                'titulo': 'Quantidade Ideal',
                'texto': 'Considere repetir 2 números do concurso anterior para maior aderência ao histórico.',
                'posicoes': []
            })

        return recomendacoes

    @staticmethod
    def resumo_para_gerador():
        """
        Retorna um resumo compacto para exibição discreta no Gerador de Palpites.
        Apenas TOP 3 posições e insight principal.
        """
        try:
            resultado = RepeticaoService.analisar_repeticoes_completo()

            if 'erro' in resultado:
                return resultado

            top3 = resultado['ranking_origem'][:3]

            return {
                'top3_posicoes_origem': top3,
                'taxa_repeticao': resultado['estatisticas']['percentual_com_repeticao'],
                'media_repeticoes': resultado['estatisticas']['media_repeticoes'],
                'insight_principal': resultado['insights'][0] if resultado['insights'] else None
            }

        except Exception as e:
            return {'erro': str(e)}

    @staticmethod
    def historico_detalhado(limite=50):
        """
        Retorna histórico detalhado das repetições nos últimos N concursos.
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(limite + 1).all()
            sorteios = list(reversed(sorteios))  # Ordenar cronologicamente

            if len(sorteios) < 2:
                return {'erro': 'Dados insuficientes'}

            historico = []

            for i in range(1, len(sorteios)):
                anterior = sorteios[i - 1]
                atual = sorteios[i]

                numeros_anterior = [
                    anterior.posicao_1, anterior.posicao_2, anterior.posicao_3,
                    anterior.posicao_4, anterior.posicao_5, anterior.posicao_6,
                    anterior.posicao_7
                ]

                numeros_atual = [
                    atual.posicao_1, atual.posicao_2, atual.posicao_3,
                    atual.posicao_4, atual.posicao_5, atual.posicao_6,
                    atual.posicao_7
                ]

                set_anterior = set(numeros_anterior)

                repeticoes = []
                for pos, num in enumerate(numeros_atual, 1):
                    if num in set_anterior:
                        pos_origem = numeros_anterior.index(num) + 1
                        repeticoes.append({
                            'numero': num,
                            'posicao_origem': pos_origem,
                            'posicao_destino': pos
                        })

                historico.append({
                    'concurso': atual.concurso,
                    'data': atual.data_sorteio.strftime('%d/%m/%Y') if atual.data_sorteio else None,
                    'mes_sorte': RepeticaoService.MESES_NOMES.get(atual.mes_sorte, str(atual.mes_sorte)),
                    'numeros_anterior': numeros_anterior,
                    'numeros_atual': numeros_atual,
                    'qtd_repeticoes': len(repeticoes),
                    'repeticoes': repeticoes
                })

            return {
                'historico': list(reversed(historico)),  # Mais recente primeiro
                'total': len(historico)
            }

        except Exception as e:
            return {'erro': str(e)}
