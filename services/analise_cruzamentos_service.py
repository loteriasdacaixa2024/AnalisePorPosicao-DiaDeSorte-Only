"""
================================================================================
SERVIÇO: Análise de Cruzamentos - DIA DE SORTE
================================================================================
Módulo ISOLADO para cruzamentos estatísticos avançados.

ANÁLISES DISPONÍVEIS:
✅ 1. Coluna × Linha (Mapa de Calor 2D) - IMPLEMENTADA
🔜 2. Coluna × Pares/Ímpares
🔜 3. Coluna × Quentes/Frias/Atrasadas
🔜 4. Coluna × Padrão de Dígitos
🔜 5. Coluna × Sequências/Finais Iguais
🔜 6. Coluna × Números Juntos
🔜 7. Coluna × Soma Total
🔜 8. Coluna × Dia da Semana
🔜 9. Coluna × Mês da Sorte

Destino: services/analise_cruzamentos_service.py
================================================================================
"""

import sqlite3
from config import Config
from collections import defaultdict


class AnaliseCruzamentosService:
    """Serviço isolado para análises de cruzamentos estatísticos"""

    # ==========================================================================
    # CONFIGURAÇÃO
    # ==========================================================================

    @staticmethod
    def _get_db_path():
        """Retorna caminho do banco"""
        import os
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analise_por_posicao.db")

    # ==========================================================================
    # CORES HEATMAP - IDENTIDADE VISUAL DIA DE SORTE (#D4B31A)
    # ==========================================================================

    # Gradiente de 0% a 100% baseado em #D4B31A (dourado)
    HEATMAP_CORES = [
        '#FFF9E6',  # 0-10%   - Creme muito claro
        '#FFF3CC',  # 10-20%  - Creme claro
        '#FFECB3',  # 20-30%  - Amarelo pálido
        '#FFE599',  # 30-40%  - Amarelo claro
        '#FFDD80',  # 40-50%  - Amarelo médio
        '#F5D066',  # 50-60%  - Dourado claro
        '#EBC94D',  # 60-70%  - Dourado médio
        '#E0C133',  # 70-80%  - Dourado
        '#D4B31A',  # 80-90%  - Dourado intenso (COR PRINCIPAL)
        '#C4A510',  # 90-100% - Dourado escuro
    ]

    @staticmethod
    def obter_cor_heatmap(percentual):
        """Retorna cor do heatmap baseado no percentual (0-100)"""
        if percentual <= 0:
            return AnaliseCruzamentosService.HEATMAP_CORES[0]

        indice = min(int(percentual / 10), 9)
        return AnaliseCruzamentosService.HEATMAP_CORES[indice]

    # ==========================================================================
    # MAPEAMENTO DO VOLANTE
    # ==========================================================================

    # Estrutura do volante Dia de Sorte (31 números em 4 linhas × 10 colunas)
    VOLANTE_ESTRUTURA = {
        # Linha 1: 01-10
        1: {'linha': 1, 'coluna': 1},
        2: {'linha': 1, 'coluna': 2},
        3: {'linha': 1, 'coluna': 3},
        4: {'linha': 1, 'coluna': 4},
        5: {'linha': 1, 'coluna': 5},
        6: {'linha': 1, 'coluna': 6},
        7: {'linha': 1, 'coluna': 7},
        8: {'linha': 1, 'coluna': 8},
        9: {'linha': 1, 'coluna': 9},
        10: {'linha': 1, 'coluna': 10},
        # Linha 2: 11-20
        11: {'linha': 2, 'coluna': 1},
        12: {'linha': 2, 'coluna': 2},
        13: {'linha': 2, 'coluna': 3},
        14: {'linha': 2, 'coluna': 4},
        15: {'linha': 2, 'coluna': 5},
        16: {'linha': 2, 'coluna': 6},
        17: {'linha': 2, 'coluna': 7},
        18: {'linha': 2, 'coluna': 8},
        19: {'linha': 2, 'coluna': 9},
        20: {'linha': 2, 'coluna': 10},
        # Linha 3: 21-30
        21: {'linha': 3, 'coluna': 1},
        22: {'linha': 3, 'coluna': 2},
        23: {'linha': 3, 'coluna': 3},
        24: {'linha': 3, 'coluna': 4},
        25: {'linha': 3, 'coluna': 5},
        26: {'linha': 3, 'coluna': 6},
        27: {'linha': 3, 'coluna': 7},
        28: {'linha': 3, 'coluna': 8},
        29: {'linha': 3, 'coluna': 9},
        30: {'linha': 3, 'coluna': 10},
        # Linha 4: apenas 31
        31: {'linha': 4, 'coluna': 1},
    }

    # ==========================================================================
    # ✅ ANÁLISE 1: COLUNA × LINHA (MAPA DE CALOR 2D)
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_linha():
        """
        Cruza análise de COLUNAS × LINHAS para gerar mapa de calor 2D do volante.

        RETORNA:
        - Frequência de cada número (1-31)
        - Frequência por linha (1-4)
        - Frequência por coluna (1-10)
        - Mapa de calor 2D com cores
        - TOP 10 números mais frequentes
        - Regiões quentes/frias
        - Insights e Recomendações
        """
        db_path = AnaliseCruzamentosService._get_db_path()

        try:
            # Buscar todos os sorteios
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum sorteio encontrado no banco'
                }

            # =================================================================
            # CONTAGEM DE FREQUÊNCIAS
            # =================================================================

            # Frequência de cada número (1-31)
            freq_numeros = defaultdict(int)

            # Frequência por linha (1-4)
            freq_linhas = defaultdict(int)

            # Frequência por coluna (1-10)
            freq_colunas = defaultdict(int)

            # Contagem de aparições por posição (linha × coluna)
            freq_posicoes = defaultdict(int)

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                for num in numeros:
                    if num in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                        estrutura = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[num]
                        linha = estrutura['linha']
                        coluna = estrutura['coluna']

                        freq_numeros[num] += 1
                        freq_linhas[linha] += 1
                        freq_colunas[coluna] += 1
                        freq_posicoes[(linha, coluna)] += 1

            # =================================================================
            # CALCULAR PERCENTUAIS
            # =================================================================

            # Percentual de cada número
            numeros_data = []
            max_freq = max(freq_numeros.values()) if freq_numeros else 1

            for num in range(1, 32):
                freq = freq_numeros.get(num, 0)
                percentual = (freq / max_freq) * 100 if max_freq > 0 else 0
                estrutura = AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(num, {})

                numeros_data.append({
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round(percentual, 2),
                    'percentual_total': round((freq / total_sorteios) * 100, 2),
                    'linha': estrutura.get('linha', 0),
                    'coluna': estrutura.get('coluna', 0),
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            # Ordenar por frequência para ranking
            numeros_ordenados = sorted(numeros_data, key=lambda x: x['frequencia'], reverse=True)

            # =================================================================
            # ESTATÍSTICAS POR LINHA
            # =================================================================

            linhas_data = []
            max_freq_linha = max(freq_linhas.values()) if freq_linhas else 1

            for linha in range(1, 5):
                freq = freq_linhas.get(linha, 0)
                percentual = (freq / max_freq_linha) * 100 if max_freq_linha > 0 else 0

                # Números desta linha
                nums_linha = [n for n in range(1, 32) if AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(n, {}).get('linha') == linha]

                linhas_data.append({
                    'linha': linha,
                    'frequencia': freq,
                    'percentual': round(percentual, 2),
                    'percentual_total': round((freq / (total_sorteios * 7)) * 100, 2),
                    'numeros': nums_linha,
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            # =================================================================
            # ESTATÍSTICAS POR COLUNA
            # =================================================================

            colunas_data = []
            max_freq_coluna = max(freq_colunas.values()) if freq_colunas else 1

            for coluna in range(1, 11):
                freq = freq_colunas.get(coluna, 0)
                percentual = (freq / max_freq_coluna) * 100 if max_freq_coluna > 0 else 0

                # Números desta coluna
                nums_coluna = [n for n in range(1, 32) if AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(n, {}).get('coluna') == coluna]

                colunas_data.append({
                    'coluna': coluna,
                    'frequencia': freq,
                    'percentual': round(percentual, 2),
                    'percentual_total': round((freq / (total_sorteios * 7)) * 100, 2),
                    'numeros': nums_coluna,
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            # Ordenar colunas por frequência
            colunas_ordenadas = sorted(colunas_data, key=lambda x: x['frequencia'], reverse=True)

            # =================================================================
            # GERAR INSIGHTS INTELIGENTES
            # =================================================================

            insights = AnaliseCruzamentosService._gerar_insights_coluna_x_linha(
                numeros_ordenados, linhas_data, colunas_ordenadas, total_sorteios
            )

            # =================================================================
            # GERAR RECOMENDAÇÕES ESTRATÉGICAS
            # =================================================================

            recomendacoes = AnaliseCruzamentosService._gerar_recomendacoes_coluna_x_linha(
                numeros_ordenados, linhas_data, colunas_ordenadas
            )

            # =================================================================
            # MONTAR VOLANTE 2D (MAPA DE CALOR)
            # =================================================================

            volante_2d = []
            for linha in range(1, 5):
                linha_data = []
                for coluna in range(1, 11):
                    # Encontrar número nesta posição
                    num = None
                    for n, estrutura in AnaliseCruzamentosService.VOLANTE_ESTRUTURA.items():
                        if estrutura['linha'] == linha and estrutura['coluna'] == coluna:
                            num = n
                            break

                    if num:
                        num_info = next((x for x in numeros_data if x['numero'] == num), None)
                        if num_info:
                            linha_data.append(num_info)
                        else:
                            linha_data.append({'numero': None, 'vazio': True})
                    else:
                        linha_data.append({'numero': None, 'vazio': True})

                volante_2d.append(linha_data)

            # =================================================================
            # TOP RANKING (TOP 10)
            # =================================================================

            top_ranking = []
            for i, num in enumerate(numeros_ordenados[:10]):
                top_ranking.append({
                    'posicao': i + 1,
                    'numero': num['numero'],
                    'frequencia': num['frequencia'],
                    'percentual': num['percentual_total'],
                    'linha': num['linha'],
                    'coluna': num['coluna'],
                    'cor_heatmap': num['cor_heatmap']
                })

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'volante_2d': volante_2d,
                'numeros': numeros_data,
                'linhas': linhas_data,
                'colunas': colunas_data,
                'colunas_ordenadas': colunas_ordenadas,
                'top_ranking': top_ranking,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro: {str(e)}'
            }

    @staticmethod
    def _gerar_insights_coluna_x_linha(numeros, linhas, colunas, total):
        """Gera insights inteligentes para a análise Coluna × Linha"""

        insights = []

        # TOP 1 número
        top1 = numeros[0]
        insights.append({
            'icone': '🏆',
            'titulo': 'Número Campeão',
            'texto': f'O número <strong>{top1["numero"]:02d}</strong> é o mais sorteado, '
                    f'aparecendo em <strong>{top1["percentual_total"]}%</strong> dos concursos. '
                    f'Está na Linha {top1["linha"]} e Coluna {top1["coluna"]}.'
        })

        # Linha mais quente
        linha_top = max(linhas, key=lambda x: x['frequencia'])
        insights.append({
            'icone': '📊',
            'titulo': 'Linha Mais Quente',
            'texto': f'A <strong>Linha {linha_top["linha"]}</strong> '
                    f'(números {", ".join([str(n).zfill(2) for n in linha_top["numeros"][:5]])}) '
                    f'concentra <strong>{linha_top["percentual_total"]}%</strong> das aparições.'
        })

        # Coluna mais quente
        coluna_top = colunas[0]
        insights.append({
            'icone': '🔥',
            'titulo': 'Coluna Dominante',
            'texto': f'A <strong>Coluna {coluna_top["coluna"]}</strong> lidera o ranking, '
                    f'com seus números aparecendo em <strong>{coluna_top["percentual_total"]}%</strong> dos sorteios.'
        })

        # Diferença entre extremos
        num_top = numeros[0]
        num_bottom = numeros[-1]
        diferenca = num_top['frequencia'] - num_bottom['frequencia']
        insights.append({
            'icone': '⚖️',
            'titulo': 'Amplitude de Frequência',
            'texto': f'Existe uma diferença de <strong>{diferenca}</strong> aparições entre o '
                    f'número mais quente ({num_top["numero"]:02d}) e o mais frio ({num_bottom["numero"]:02d}).'
        })

        # Região quente
        # Identificar quadrante mais forte
        q1 = sum(n['frequencia'] for n in numeros if n['linha'] <= 2 and n['coluna'] <= 5)
        q2 = sum(n['frequencia'] for n in numeros if n['linha'] <= 2 and n['coluna'] > 5)
        q3 = sum(n['frequencia'] for n in numeros if n['linha'] > 2 and n['coluna'] <= 5)
        q4 = sum(n['frequencia'] for n in numeros if n['linha'] > 2 and n['coluna'] > 5)

        quadrantes = {'Superior-Esquerdo': q1, 'Superior-Direito': q2, 'Inferior-Esquerdo': q3, 'Inferior-Direito': q4}
        melhor_quad = max(quadrantes, key=quadrantes.get)

        insights.append({
            'icone': '🎯',
            'titulo': 'Região Mais Forte',
            'texto': f'O quadrante <strong>{melhor_quad}</strong> do volante concentra mais dezenas sorteadas. '
                    f'Foque nessa região para aumentar suas chances.'
        })

        # Coluna com 4 números vs 3
        insights.append({
            'icone': '💡',
            'titulo': 'Vantagem da Coluna 1',
            'texto': f'A Coluna 1 tem <strong>4 números</strong> (01, 11, 21, 31) enquanto as demais têm 3. '
                    f'Isso explica parte de sua liderança estatística.'
        })

        return insights

    @staticmethod
    def _gerar_recomendacoes_coluna_x_linha(numeros, linhas, colunas):
        """Gera recomendações estratégicas"""

        recomendacoes = []

        # Top 5 números
        top5 = numeros[:5]
        top5_nums = ', '.join([f'{n["numero"]:02d}' for n in top5])

        recomendacoes.append({
            'numero': '1',
            'titulo': 'Inclua os TOP 5 Números',
            'texto': 'Em toda aposta, considere incluir pelo menos 2-3 destes números mais frequentes:',
            'destaque': f'TOP 5: {top5_nums}'
        })

        # Balanceamento por linha
        recomendacoes.append({
            'numero': '2',
            'titulo': 'Distribua Entre Linhas',
            'texto': 'Para um jogo equilibrado, escolha números de pelo menos 3 linhas diferentes do volante.',
            'destaque': 'Ideal: 2-3 da L1, 2-3 da L2, 1-2 da L3'
        })

        # Colunas TOP
        top3_colunas = colunas[:3]
        colunas_str = ', '.join([str(c['coluna']) for c in top3_colunas])

        recomendacoes.append({
            'numero': '3',
            'titulo': 'Foque nas Colunas Campeãs',
            'texto': 'As colunas mais frequentes historicamente devem ter representação em seu jogo:',
            'destaque': f'Colunas TOP: {colunas_str}'
        })

        # Evitar números frios
        bottom5 = numeros[-5:]
        bottom5_nums = ', '.join([f'{n["numero"]:02d}' for n in bottom5])

        recomendacoes.append({
            'numero': '4',
            'titulo': 'Cuidado com os Frios',
            'texto': 'Estes números aparecem menos. Use no máximo 1 por jogo como "azarão":',
            'destaque': f'Mais frios: {bottom5_nums}'
        })

        # Estratégia final
        recomendacoes.append({
            'numero': '5',
            'titulo': 'Estratégia do Mapa de Calor',
            'texto': 'Use o mapa visual acima para escolher números de regiões QUENTES (cores intensas) e equilibrar com algumas regiões MÉDIAS.',
            'destaque': '🟨 Dourado intenso = QUENTE | 🟫 Creme = FRIO'
        })

        return recomendacoes

    # ==========================================================================
    # ✅ ANÁLISE 2: COLUNA × PARES/ÍMPARES
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_pares_impares():
        """
        Cruza análise de COLUNAS × PARES/ÍMPARES.
        Verifica se cada coluna tende a puxar mais pares ou ímpares.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            # Contagem por coluna
            colunas_stats = {}
            for col in range(1, 11):
                colunas_stats[col] = {'pares': 0, 'impares': 0, 'total': 0}

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                for num in numeros:
                    if num in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                        coluna = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[num]['coluna']
                        colunas_stats[coluna]['total'] += 1
                        if num % 2 == 0:
                            colunas_stats[coluna]['pares'] += 1
                        else:
                            colunas_stats[coluna]['impares'] += 1

            # Montar resultado
            resultado = []
            for col in range(1, 11):
                stats = colunas_stats[col]
                total = stats['total'] or 1
                pct_pares = round((stats['pares'] / total) * 100, 2)
                pct_impares = round((stats['impares'] / total) * 100, 2)
                tendencia = 'PARES' if pct_pares > pct_impares else 'ÍMPARES'

                resultado.append({
                    'coluna': col,
                    'pares': stats['pares'],
                    'impares': stats['impares'],
                    'pct_pares': pct_pares,
                    'pct_impares': pct_impares,
                    'tendencia': tendencia,
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(pct_pares)
                })

            # Insights
            col_mais_pares = max(resultado, key=lambda x: x['pct_pares'])
            col_mais_impares = max(resultado, key=lambda x: x['pct_impares'])

            insights = [
                {
                    'icone': '🔢',
                    'titulo': 'Coluna Mais Par',
                    'texto': f'A <strong>Coluna {col_mais_pares["coluna"]}</strong> tem maior tendência a números pares ({col_mais_pares["pct_pares"]}%).'
                },
                {
                    'icone': '🔵',
                    'titulo': 'Coluna Mais Ímpar',
                    'texto': f'A <strong>Coluna {col_mais_impares["coluna"]}</strong> tem maior tendência a números ímpares ({col_mais_impares["pct_impares"]}%).'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Equilibre Pares e Ímpares',
                    'texto': 'Para um jogo balanceado, busque 3-4 pares e 3-4 ímpares nas 7 dezenas.',
                    'destaque': 'Proporção ideal: 4 pares + 3 ímpares ou 3 pares + 4 ímpares'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'colunas': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 3: COLUNA × QUENTES/FRIAS/ATRASADAS
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_quentes_frias(ultimos_n=50):
        """
        Cruza análise de COLUNAS × NÚMEROS QUENTES/FRIOS.
        Quentes = mais sorteados nos últimos N concursos.
        Frios = menos sorteados.
        Atrasados = mais tempo sem sair.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            ultimos = sorteios[:ultimos_n]
            ultimo_concurso = sorteios[0].concurso if sorteios else 0

            # Frequência nos últimos N
            freq_recente = defaultdict(int)
            ultima_aparicao = {}

            for idx, sorteio in enumerate(sorteios):
                numeros = sorteio.get_posicoes_lista()
                for num in numeros:
                    if num not in ultima_aparicao:
                        ultima_aparicao[num] = sorteio.concurso
                    if idx < ultimos_n:
                        freq_recente[num] += 1

            # Classificar números
            numeros_stats = []
            max_freq = max(freq_recente.values()) if freq_recente else 1

            for num in range(1, 32):
                freq = freq_recente.get(num, 0)
                atraso = ultimo_concurso - ultima_aparicao.get(num, ultimo_concurso)
                percentual = (freq / max_freq) * 100 if max_freq > 0 else 0

                if freq >= max_freq * 0.7:
                    status = 'QUENTE'
                elif freq <= max_freq * 0.3:
                    status = 'FRIO'
                else:
                    status = 'MORNO'

                estrutura = AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(num, {})

                numeros_stats.append({
                    'numero': num,
                    'frequencia_recente': freq,
                    'atraso': atraso,
                    'status': status,
                    'coluna': estrutura.get('coluna', 0),
                    'linha': estrutura.get('linha', 0),
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            # Agrupar por coluna
            colunas_status = {}
            for col in range(1, 11):
                nums_col = [n for n in numeros_stats if n['coluna'] == col]
                quentes = len([n for n in nums_col if n['status'] == 'QUENTE'])
                frios = len([n for n in nums_col if n['status'] == 'FRIO'])
                mornos = len([n for n in nums_col if n['status'] == 'MORNO'])

                colunas_status[col] = {
                    'coluna': col,
                    'quentes': quentes,
                    'frios': frios,
                    'mornos': mornos,
                    'numeros': nums_col
                }

            # Top quentes e frios
            quentes_ordenados = sorted(numeros_stats, key=lambda x: x['frequencia_recente'], reverse=True)[:10]
            frios_ordenados = sorted(numeros_stats, key=lambda x: x['frequencia_recente'])[:10]
            atrasados = sorted(numeros_stats, key=lambda x: x['atraso'], reverse=True)[:10]

            insights = [
                {
                    'icone': '🔥',
                    'titulo': f'TOP 3 Quentes (últimos {ultimos_n})',
                    'texto': f'Números mais sorteados recentemente: <strong>{", ".join([f"{n["numero"]:02d}" for n in quentes_ordenados[:3]])}</strong>'
                },
                {
                    'icone': '❄️',
                    'titulo': 'TOP 3 Frios',
                    'texto': f'Números menos sorteados: <strong>{", ".join([f"{n["numero"]:02d}" for n in frios_ordenados[:3]])}</strong>'
                },
                {
                    'icone': '⏰',
                    'titulo': 'Mais Atrasados',
                    'texto': f'Maior tempo sem sair: <strong>{", ".join([f"{n["numero"]:02d} ({n["atraso"]} concursos)" for n in atrasados[:3]])}</strong>'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Priorize os Quentes',
                    'texto': 'Números quentes estão em fase de alta. Inclua 3-4 deles no seu jogo.',
                    'destaque': f'Quentes: {", ".join([f"{n["numero"]:02d}" for n in quentes_ordenados[:5]])}'
                },
                {
                    'numero': '2',
                    'titulo': 'Atrasados como Azarão',
                    'texto': 'Números muito atrasados podem "estar devendo". Use 1 como aposta de risco.',
                    'destaque': f'Atrasados: {", ".join([f"{n["numero"]:02d}" for n in atrasados[:3]])}'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'ultimos_analisados': ultimos_n,
                'numeros': numeros_stats,
                'colunas': list(colunas_status.values()),
                'top_quentes': quentes_ordenados,
                'top_frios': frios_ordenados,
                'top_atrasados': atrasados,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 4: COLUNA × PADRÃO DÍGITOS
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_padrao_digitos():
        """
        Cruza análise de COLUNAS × PADRÃO DE DÍGITOS.
        Analisa quantos números de cada dígito final (0-9) aparecem por coluna.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            # Contagem por dígito final e coluna
            digitos_por_coluna = {}
            for col in range(1, 11):
                digitos_por_coluna[col] = defaultdict(int)

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                for num in numeros:
                    if num in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                        coluna = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[num]['coluna']
                        digito_final = num % 10
                        digitos_por_coluna[coluna][digito_final] += 1

            # Montar resultado
            resultado = []
            for col in range(1, 11):
                digitos = digitos_por_coluna[col]
                total = sum(digitos.values()) or 1
                digito_top = max(digitos.items(), key=lambda x: x[1]) if digitos else (0, 0)

                resultado.append({
                    'coluna': col,
                    'digitos': dict(digitos),
                    'digito_dominante': digito_top[0],
                    'freq_dominante': digito_top[1],
                    'pct_dominante': round((digito_top[1] / total) * 100, 2)
                })

            insights = [
                {
                    'icone': '🔢',
                    'titulo': 'Padrão de Dígitos',
                    'texto': 'Cada coluna tem números com dígitos finais específicos. A Coluna 1 tem números terminados em 1 (01, 11, 21, 31).'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Varie os Finais',
                    'texto': 'Tente incluir números com diferentes dígitos finais para aumentar a cobertura.',
                    'destaque': 'Ideal: pelo menos 5 dígitos finais diferentes'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'colunas': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 5: COLUNA × SEQUÊNCIAS
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_sequencias():
        """
        Cruza análise de COLUNAS × SEQUÊNCIAS CONSECUTIVAS.
        Verifica quantas vezes cada coluna participa de sequências (ex: 01-02, 11-12).
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            # Contagem de sequências por coluna
            seq_por_coluna = defaultdict(int)
            jogos_com_seq = 0

            for sorteio in sorteios:
                numeros = sorted(sorteio.get_posicoes_lista())
                tem_seq = False
                for i in range(len(numeros) - 1):
                    if numeros[i + 1] - numeros[i] == 1:
                        tem_seq = True
                        # Pegar coluna do primeiro número da sequência
                        if numeros[i] in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                            col = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[numeros[i]]['coluna']
                            seq_por_coluna[col] += 1
                if tem_seq:
                    jogos_com_seq += 1

            # Montar resultado
            resultado = []
            max_seq = max(seq_por_coluna.values()) if seq_por_coluna else 1

            for col in range(1, 11):
                freq = seq_por_coluna.get(col, 0)
                percentual = (freq / max_seq) * 100 if max_seq > 0 else 0

                resultado.append({
                    'coluna': col,
                    'sequencias': freq,
                    'percentual': round(percentual, 2),
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            pct_jogos_seq = round((jogos_com_seq / total_sorteios) * 100, 2)

            insights = [
                {
                    'icone': '🔗',
                    'titulo': 'Frequência de Sequências',
                    'texto': f'<strong>{pct_jogos_seq}%</strong> dos sorteios têm pelo menos uma sequência consecutiva (ex: 05-06).'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Inclua pelo menos 1 Sequência',
                    'texto': 'A maioria dos jogos vencedores tem ao menos um par consecutivo.',
                    'destaque': f'{pct_jogos_seq}% dos sorteios têm sequências'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'jogos_com_sequencia': jogos_com_seq,
                'pct_jogos_sequencia': pct_jogos_seq,
                'colunas': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 6: COLUNA × NÚMEROS JUNTOS
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_numeros_juntos():
        """
        Cruza análise de COLUNAS × PARES DE NÚMEROS QUE MAIS SAEM JUNTOS.
        Identifica duplas frequentes dentro de cada coluna.
        """
        try:
            from models.sorteio import Sorteio
            from itertools import combinations
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            # Contagem de pares
            pares_contagem = defaultdict(int)

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                for par in combinations(sorted(numeros), 2):
                    pares_contagem[par] += 1

            # Top 20 pares
            top_pares = sorted(pares_contagem.items(), key=lambda x: x[1], reverse=True)[:20]

            resultado = []
            for par, freq in top_pares:
                col1 = AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(par[0], {}).get('coluna', 0)
                col2 = AnaliseCruzamentosService.VOLANTE_ESTRUTURA.get(par[1], {}).get('coluna', 0)

                resultado.append({
                    'numero1': par[0],
                    'numero2': par[1],
                    'frequencia': freq,
                    'percentual': round((freq / total_sorteios) * 100, 2),
                    'coluna1': col1,
                    'coluna2': col2,
                    'mesma_coluna': col1 == col2
                })

            insights = [
                {
                    'icone': '🤝',
                    'titulo': 'Dupla Campeã',
                    'texto': f'Os números <strong>{resultado[0]["numero1"]:02d}</strong> e <strong>{resultado[0]["numero2"]:02d}</strong> aparecem juntos em {resultado[0]["percentual"]}% dos sorteios.' if resultado else 'Sem dados'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Use Duplas Fortes',
                    'texto': 'Inclua pelo menos uma das duplas mais frequentes no seu jogo.',
                    'destaque': f'TOP: {resultado[0]["numero1"]:02d}-{resultado[0]["numero2"]:02d}, {resultado[1]["numero1"]:02d}-{resultado[1]["numero2"]:02d}' if len(resultado) >= 2 else 'Sem dados'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'top_pares': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 7: COLUNA × SOMA
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_soma():
        """
        Cruza análise de COLUNAS × SOMA TOTAL DO JOGO.
        Identifica faixas de soma mais frequentes.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            # Calcular somas
            somas = []
            faixas = defaultdict(int)

            for sorteio in sorteios:
                numeros = sorteio.get_posicoes_lista()
                soma = sum(numeros)
                somas.append(soma)

                # Classificar em faixas de 10
                faixa = (soma // 10) * 10
                faixas[f'{faixa}-{faixa+9}'] += 1

            soma_media = round(sum(somas) / len(somas), 2)
            soma_min = min(somas)
            soma_max = max(somas)

            # Ordenar faixas
            faixas_ordenadas = sorted(faixas.items(), key=lambda x: x[1], reverse=True)

            resultado_faixas = []
            max_freq = faixas_ordenadas[0][1] if faixas_ordenadas else 1

            for faixa, freq in faixas_ordenadas:
                percentual = (freq / max_freq) * 100
                resultado_faixas.append({
                    'faixa': faixa,
                    'frequencia': freq,
                    'percentual': round((freq / total_sorteios) * 100, 2),
                    'cor_heatmap': AnaliseCruzamentosService.obter_cor_heatmap(percentual)
                })

            insights = [
                {
                    'icone': '➕',
                    'titulo': 'Soma Média',
                    'texto': f'A soma média dos sorteios é <strong>{soma_media}</strong> (mín: {soma_min}, máx: {soma_max}).'
                },
                {
                    'icone': '📊',
                    'titulo': 'Faixa Mais Comum',
                    'texto': f'A faixa <strong>{faixas_ordenadas[0][0]}</strong> é a mais frequente, aparecendo em {resultado_faixas[0]["percentual"]}% dos sorteios.' if faixas_ordenadas else 'Sem dados'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Mire na Soma Ideal',
                    'texto': f'Monte jogos com soma entre {int(soma_media - 15)} e {int(soma_media + 15)}.',
                    'destaque': f'Faixa ideal: {int(soma_media - 15)} a {int(soma_media + 15)}'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'soma_media': soma_media,
                'soma_min': soma_min,
                'soma_max': soma_max,
                'faixas': resultado_faixas,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 8: COLUNA × DIA SEMANA
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_dia_semana():
        """
        Cruza análise de COLUNAS × DIA DA SEMANA.
        Verifica se há padrões por dia do sorteio.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            freq_por_dia = defaultdict(lambda: defaultdict(int))
            total_por_dia = defaultdict(int)

            for sorteio in sorteios:
                if sorteio.data_sorteio:
                    dia = sorteio.data_sorteio.weekday()
                    total_por_dia[dia] += 1
                    numeros = sorteio.get_posicoes_lista()
                    for num in numeros:
                        if num in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                            coluna = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[num]['coluna']
                            freq_por_dia[dia][coluna] += 1

            # Montar resultado
            resultado = []
            for dia_idx, dia_nome in enumerate(dias_semana):
                if total_por_dia[dia_idx] > 0:
                    colunas_dia = []
                    for col in range(1, 11):
                        freq = freq_por_dia[dia_idx].get(col, 0)
                        colunas_dia.append({
                            'coluna': col,
                            'frequencia': freq
                        })

                    col_top = max(colunas_dia, key=lambda x: x['frequencia'])

                    resultado.append({
                        'dia': dia_nome,
                        'dia_idx': dia_idx,
                        'total_sorteios': total_por_dia[dia_idx],
                        'colunas': colunas_dia,
                        'coluna_dominante': col_top['coluna']
                    })

            insights = [
                {
                    'icone': '📅',
                    'titulo': 'Variação por Dia',
                    'texto': 'Dia de Sorte tem sorteios em dias específicos. Analise se há padrão no seu dia preferido.'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Observe o Dia do Sorteio',
                    'texto': 'Verifique quais colunas são mais fortes no dia que você costuma apostar.',
                    'destaque': 'Cada dia pode ter tendências diferentes'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'dias': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # ✅ ANÁLISE 9: COLUNA × MÊS
    # ==========================================================================

    @staticmethod
    def analisar_coluna_x_mes():
        """
        Cruza análise de COLUNAS × MÊS DA SORTE.
        Verifica correlação entre mês sorteado e colunas das dezenas.
        """
        try:
            from models.sorteio import Sorteio
            sorteios = Sorteio.query.all()
            total_sorteios = len(sorteios)

            if total_sorteios == 0:
                return {'sucesso': False, 'mensagem': 'Nenhum sorteio encontrado'}

            meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                     'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

            freq_meses = defaultdict(int)
            mes_x_coluna = defaultdict(lambda: defaultdict(int))

            for sorteio in sorteios:
                # Tentar pegar o mês da sorte (se disponível)
                mes = getattr(sorteio, 'mes', None) or getattr(sorteio, 'mes_sorte', None)
                if mes:
                    freq_meses[mes] += 1
                    numeros = sorteio.get_posicoes_lista()
                    for num in numeros:
                        if num in AnaliseCruzamentosService.VOLANTE_ESTRUTURA:
                            coluna = AnaliseCruzamentosService.VOLANTE_ESTRUTURA[num]['coluna']
                            mes_x_coluna[mes][coluna] += 1

            # Ordenar meses por frequência
            meses_ordenados = sorted(freq_meses.items(), key=lambda x: x[1], reverse=True)

            resultado = []
            for mes, freq in meses_ordenados[:12]:
                colunas_mes = []
                for col in range(1, 11):
                    colunas_mes.append({
                        'coluna': col,
                        'frequencia': mes_x_coluna[mes].get(col, 0)
                    })

                resultado.append({
                    'mes': mes,
                    'frequencia': freq,
                    'percentual': round((freq / total_sorteios) * 100, 2),
                    'colunas': colunas_mes
                })

            insights = [
                {
                    'icone': '📆',
                    'titulo': 'Mês Mais Sorteado',
                    'texto': f'O mês <strong>{meses_ordenados[0][0]}</strong> aparece em {round((meses_ordenados[0][1] / total_sorteios) * 100, 2)}% dos sorteios.' if meses_ordenados else 'Sem dados de mês'
                }
            ]

            recomendacoes = [
                {
                    'numero': '1',
                    'titulo': 'Escolha Mês Estratégico',
                    'texto': 'Priorize os meses que aparecem com maior frequência.',
                    'destaque': f'TOP 3: {", ".join([m[0] for m in meses_ordenados[:3]])}' if len(meses_ordenados) >= 3 else 'Sem dados suficientes'
                }
            ]

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'meses': resultado,
                'insights': insights,
                'recomendacoes': recomendacoes
            }

        except Exception as e:
            return {'sucesso': False, 'mensagem': str(e)}

    # ==========================================================================
    # STATUS DAS ANÁLISES
    # ==========================================================================

    @staticmethod
    def obter_status_analises():
        """Retorna status de todas as análises disponíveis"""
        return {
            'analises': [
                {'id': 1, 'nome': 'Coluna × Linha', 'status': 'implementada', 'icone': '🔥'},
                {'id': 2, 'nome': 'Coluna × Pares/Ímpares', 'status': 'implementada', 'icone': '✅'},
                {'id': 3, 'nome': 'Coluna × Quentes/Frias', 'status': 'implementada', 'icone': '✅'},
                {'id': 4, 'nome': 'Coluna × Padrão Dígitos', 'status': 'implementada', 'icone': '✅'},
                {'id': 5, 'nome': 'Coluna × Sequências', 'status': 'implementada', 'icone': '✅'},
                {'id': 6, 'nome': 'Coluna × Números Juntos', 'status': 'implementada', 'icone': '✅'},
                {'id': 7, 'nome': 'Coluna × Soma Total', 'status': 'implementada', 'icone': '✅'},
                {'id': 8, 'nome': 'Coluna × Dia Semana', 'status': 'implementada', 'icone': '✅'},
                {'id': 9, 'nome': 'Coluna × Mês', 'status': 'implementada', 'icone': '✅'},
            ],
            'total_implementadas': 9,
            'total_pendentes': 0
        }

    # ==========================================================================
    # OBTER TODAS AS ANÁLISES DE UMA VEZ
    # ==========================================================================

    @staticmethod
    def obter_todas_analises():
        """Retorna todas as 9 análises de uma vez"""
        return {
            'analise_1_linha': AnaliseCruzamentosService.analisar_coluna_x_linha(),
            'analise_2_pares_impares': AnaliseCruzamentosService.analisar_coluna_x_pares_impares(),
            'analise_3_quentes_frias': AnaliseCruzamentosService.analisar_coluna_x_quentes_frias(),
            'analise_4_padrao_digitos': AnaliseCruzamentosService.analisar_coluna_x_padrao_digitos(),
            'analise_5_sequencias': AnaliseCruzamentosService.analisar_coluna_x_sequencias(),
            'analise_6_numeros_juntos': AnaliseCruzamentosService.analisar_coluna_x_numeros_juntos(),
            'analise_7_soma': AnaliseCruzamentosService.analisar_coluna_x_soma(),
            'analise_8_dia_semana': AnaliseCruzamentosService.analisar_coluna_x_dia_semana(),
            'analise_9_mes': AnaliseCruzamentosService.analisar_coluna_x_mes(),
        }
