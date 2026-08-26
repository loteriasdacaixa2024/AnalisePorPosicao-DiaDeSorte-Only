from models.sorteio import Sorteio, db
from collections import defaultdict, Counter
from itertools import combinations_with_replacement, combinations
from math import comb

class AnaliseDigitoPadraoInicialFinalService:

    @staticmethod
    def analisar_padroes():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        frequencia_digitos_iniciais = defaultdict(int)
        frequencia_digitos_finais = defaultdict(int)
        digitos_iniciais_por_posicao = defaultdict(lambda: defaultdict(int))
        digitos_finais_por_posicao = defaultdict(lambda: defaultdict(int))
        padroes_iniciais_lista = []
        padroes_finais_lista = []

        for sorteio in sorteios:
            digitos_iniciais_concurso = defaultdict(int)
            digitos_finais_concurso = defaultdict(int)

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    digito_inicial = numero // 10
                    digito_final = numero % 10

                    frequencia_digitos_iniciais[digito_inicial] += 1
                    frequencia_digitos_finais[digito_final] += 1

                    digitos_iniciais_concurso[digito_inicial] += 1
                    digitos_finais_concurso[digito_final] += 1

                    digitos_iniciais_por_posicao[posicao][digito_inicial] += 1
                    digitos_finais_por_posicao[posicao][digito_final] += 1

            padrao_inicial = '-'.join([str(digitos_iniciais_concurso.get(d, 0)) for d in range(4)])
            padrao_final = '-'.join([str(digitos_finais_concurso.get(d, 0)) for d in range(10)])

            padroes_iniciais_lista.append(padrao_inicial)
            padroes_finais_lista.append(padrao_final)

        total_numeros_sorteados = total_concursos * 7

        analise_digitos_iniciais = []
        for digito in range(4):
            freq = frequencia_digitos_iniciais.get(digito, 0)
            percentual = round((freq / total_numeros_sorteados * 100), 2)

            if digito == 0:
                faixa = "0 (01-09)"
                total_numeros_faixa = 9
            elif digito == 1:
                faixa = "1 (10-19)"
                total_numeros_faixa = 10
            elif digito == 2:
                faixa = "2 (20-29)"
                total_numeros_faixa = 10
            else:
                faixa = "3 (30-31)"
                total_numeros_faixa = 2

            percentual_esperado = round((total_numeros_faixa / 31 * 100), 2)
            diferenca = round(percentual - percentual_esperado, 2)

            if diferenca > 5:
                status = "Acima do Esperado"
            elif diferenca < -5:
                status = "Abaixo do Esperado"
            else:
                status = "Dentro do Esperado"

            analise_digitos_iniciais.append({
                'digito': digito,
                'faixa': faixa,
                'frequencia': freq,
                'porcentagem': percentual,
                'percentual_esperado': percentual_esperado,
                'diferenca': diferenca,
                'status': status
            })

        analise_digitos_finais = []
        for digito in range(10):
            freq = frequencia_digitos_finais.get(digito, 0)
            percentual = round((freq / total_numeros_sorteados * 100), 2)
            percentual_esperado = 10.0
            diferenca = round(percentual - percentual_esperado, 2)

            if diferenca > 2:
                status = "Acima do Esperado"
            elif diferenca < -2:
                status = "Abaixo do Esperado"
            else:
                status = "Dentro do Esperado"

            analise_digitos_finais.append({
                'digito': digito,
                'frequencia': freq,
                'porcentagem': percentual,
                'percentual_esperado': percentual_esperado,
                'diferenca': diferenca,
                'status': status
            })

        analise_inicial_por_posicao = {}
        for posicao in range(1, 8):
            lista_digitos = []
            for digito in range(4):
                freq = digitos_iniciais_por_posicao[posicao].get(digito, 0)
                percentual = round((freq / total_concursos * 100), 2)
                lista_digitos.append({
                    'digito': digito,
                    'frequencia': freq,
                    'porcentagem': percentual
                })
            analise_inicial_por_posicao[str(posicao)] = lista_digitos

        analise_final_por_posicao = {}
        for posicao in range(1, 8):
            lista_digitos = []
            for digito in range(10):
                freq = digitos_finais_por_posicao[posicao].get(digito, 0)
                percentual = round((freq / total_concursos * 100), 2)
                lista_digitos.append({
                    'digito': digito,
                    'frequencia': freq,
                    'porcentagem': percentual
                })
            analise_final_por_posicao[str(posicao)] = lista_digitos

        padroes_iniciais_com_concursos = defaultdict(list)
        for idx, padrao in enumerate(padroes_iniciais_lista):
            sorteio = sorteios[idx]
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            padroes_iniciais_com_concursos[padrao].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros)
            })

        frequencia_padroes_iniciais = {padrao: len(concursos) for padrao, concursos in padroes_iniciais_com_concursos.items()}
        top_padroes_iniciais = sorted(frequencia_padroes_iniciais.items(), key=lambda x: x[1], reverse=True)[:10]

        padroes_iniciais_formatados = []
        for padrao, freq in top_padroes_iniciais:
            partes = padrao.split('-')
            descricao = f"0:{partes[0]} | 1:{partes[1]} | 2:{partes[2]} | 3:{partes[3]}"
            percentual = round((freq / total_concursos * 100), 2)
            padroes_iniciais_formatados.append({
                'padrao': descricao,
                'frequencia': freq,
                'porcentagem': percentual,
                'concursos': padroes_iniciais_com_concursos[padrao]
            })

        padroes_finais_com_concursos = defaultdict(list)
        for idx, padrao in enumerate(padroes_finais_lista):
            sorteio = sorteios[idx]
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            padroes_finais_com_concursos[padrao].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros)
            })

        frequencia_padroes_finais = {padrao: len(concursos) for padrao, concursos in padroes_finais_com_concursos.items()}
        top_padroes_finais = sorted(frequencia_padroes_finais.items(), key=lambda x: x[1], reverse=True)[:10]

        padroes_finais_formatados = []
        for padrao, freq in top_padroes_finais:
            partes = padrao.split('-')
            descricao = f"0:{partes[0]} | 1:{partes[1]} | 2:{partes[2]} | 3:{partes[3]} | 4:{partes[4]} | 5:{partes[5]} | 6:{partes[6]} | 7:{partes[7]} | 8:{partes[8]} | 9:{partes[9]}"
            percentual = round((freq / total_concursos * 100), 2)
            padroes_finais_formatados.append({
                'padrao': descricao,
                'frequencia': freq,
                'porcentagem': percentual,
                'concursos': padroes_finais_com_concursos[padrao]
            })

        # NOVA FUNCIONALIDADE: Padrões de dígitos iniciais no formato "0 1 1 2 2 3 3"
        padroes_digitos_iniciais_formatados = []
        padroes_digitos_iniciais_simples = []

        for idx, sorteio in enumerate(sorteios):
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            if numeros:
                # Extrair dígitos iniciais dos números (primeiro dígito de cada número)
                digitos_iniciais = [str(numero // 10) for numero in sorted(numeros)]
                padrao_simples = ' '.join(digitos_iniciais)
                padroes_digitos_iniciais_simples.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': sorted(numeros),
                    'digitos_iniciais': digitos_iniciais,
                    'padrao': padrao_simples
                })

        # Contar frequência dos padrões simples
        from collections import Counter
        frequencia_padroes_simples = Counter(item['padrao'] for item in padroes_digitos_iniciais_simples)
        top_padroes_simples = frequencia_padroes_simples.most_common(10)

        for padrao, freq in top_padroes_simples:
            concursos_com_padrao = [item for item in padroes_digitos_iniciais_simples if item['padrao'] == padrao]
            percentual = round((freq / total_concursos * 100), 2)

            padroes_digitos_iniciais_formatados.append({
                'padrao': padrao,
                'frequencia': freq,
                'porcentagem': percentual,
                'concursos': concursos_com_padrao
            })

        return {
            'total_concursos': total_concursos,
            'total_numeros_sorteados': total_numeros_sorteados,
            'analise_digitos_iniciais': analise_digitos_iniciais,
            'analise_digitos_finais': analise_digitos_finais,
            'analise_inicial_por_posicao': analise_inicial_por_posicao,
            'analise_final_por_posicao': analise_final_por_posicao,
            'top_padroes_iniciais': padroes_iniciais_formatados,
            'top_padroes_finais': padroes_finais_formatados,
            'top_padroes_digitos_iniciais_simples': padroes_digitos_iniciais_formatados  # NOVA FUNCIONALIDADE
        }

    @staticmethod
    def calcular_frequencia_campea(padroes_formatados, tipo='inicial'):
        """
        Identifica o padrão campeão em frequência e retorna ranking completo

        Args:
            padroes_formatados: Lista de padrões já formatados com frequência
            tipo: 'inicial' ou 'final'

        Returns:
            Dicionário com campeã e ranking das 3 primeiras posições
        """
        if not padroes_formatados or len(padroes_formatados) == 0:
            return {
                'campea': None,
                'frequencia': 0,
                'posicoes': {
                    'primeiro': None,
                    'segundo': None,
                    'terceiro': None
                },
                'insights': []
            }

        # Ordenar por frequência (já deve estar ordenado, mas garantimos)
        padroes_sorted = sorted(padroes_formatados, key=lambda x: x['frequencia'], reverse=True)

        # Top 3
        primeiro = padroes_sorted[0] if len(padroes_sorted) > 0 else None
        segundo = padroes_sorted[1] if len(padroes_sorted) > 1 else None
        terceiro = padroes_sorted[2] if len(padroes_sorted) > 2 else None

        # Gerar insights inteligentes
        insights = []

        if primeiro:
            # Extrair padrão visual (exemplo: "0:2 | 1:3 | 2:2 | 3:0" -> "0 0 1 1 1 2 2")
            padrao_visual = AnaliseDigitoPadraoInicialFinalService._extrair_padrao_visual(primeiro['padrao'])

            insights.append({
                'icone': '👑',
                'titulo': 'Padrão Campeão Absoluto',
                'texto': f"O padrão <strong>{padrao_visual}</strong> domina com {primeiro['frequencia']} aparições ({primeiro['porcentagem']}% dos sorteios)",
                'cor': 'success'
            })

            # Comparação com segundo lugar
            if segundo:
                diferenca_freq = primeiro['frequencia'] - segundo['frequencia']
                percentual_a_mais = round((diferenca_freq / segundo['frequencia'] * 100), 1) if segundo['frequencia'] > 0 else 0

                insights.append({
                    'icone': '📊',
                    'titulo': 'Dominância Clara',
                    'texto': f"O campeão aparece <strong>{diferenca_freq} vezes a mais</strong> que o 2º lugar, representando {percentual_a_mais}% de vantagem",
                    'cor': 'info'
                })

            # Análise de consistência
            if primeiro['porcentagem'] > 5:
                insights.append({
                    'icone': '⚡',
                    'titulo': 'Alta Consistência',
                    'texto': f"Com {primeiro['porcentagem']}% de presença, este padrão demonstra forte tendência histórica",
                    'cor': 'warning'
                })

        resultado = {
            'campea': AnaliseDigitoPadraoInicialFinalService._extrair_padrao_visual(primeiro['padrao']) if primeiro else None,
            'frequencia': primeiro['frequencia'] if primeiro else 0,
            'porcentagem': primeiro['porcentagem'] if primeiro else 0,
            'posicoes': {
                'primeiro': {
                    'padrao': AnaliseDigitoPadraoInicialFinalService._extrair_padrao_visual(primeiro['padrao']) if primeiro else None,
                    'padrao_original': primeiro['padrao'] if primeiro else None,
                    'freq': primeiro['frequencia'] if primeiro else 0,
                    'porc': primeiro['porcentagem'] if primeiro else 0,
                    'concursos': primeiro.get('concursos', []) if primeiro else []
                },
                'segundo': {
                    'padrao': AnaliseDigitoPadraoInicialFinalService._extrair_padrao_visual(segundo['padrao']) if segundo else None,
                    'padrao_original': segundo['padrao'] if segundo else None,
                    'freq': segundo['frequencia'] if segundo else 0,
                    'porc': segundo['porcentagem'] if segundo else 0,
                    'concursos': segundo.get('concursos', []) if segundo else []
                },
                'terceiro': {
                    'padrao': AnaliseDigitoPadraoInicialFinalService._extrair_padrao_visual(terceiro['padrao']) if terceiro else None,
                    'padrao_original': terceiro['padrao'] if terceiro else None,
                    'freq': terceiro['frequencia'] if terceiro else 0,
                    'porc': terceiro['porcentagem'] if terceiro else 0,
                    'concursos': terceiro.get('concursos', []) if terceiro else []
                }
            },
            'insights': insights
        }

        return resultado

    @staticmethod
    def gerar_timeline_aparicoes(padrao_campea_original, todos_sorteios):
        """
        Gera uma timeline mostrando em quais concursos o padrão campeão apareceu ou não

        Args:
            padrao_campea_original: Padrão original no formato "0:X | 1:Y | 2:Z | 3:W"
            todos_sorteios: Lista de todos os sorteios

        Returns:
            Lista de dicionários com informações de cada concurso
        """
        timeline = []

        for sorteio in todos_sorteios:
            # Reconstruir o padrão deste sorteio
            digitos_iniciais_concurso = defaultdict(int)
            numeros_sorteio = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros_sorteio.append(numero)
                    digito_inicial = numero // 10
                    digitos_iniciais_concurso[digito_inicial] += 1

            # Criar padrão do concurso
            padrao_concurso = '-'.join([str(digitos_iniciais_concurso.get(d, 0)) for d in range(4)])

            # Formatar padrão
            partes = padrao_concurso.split('-')
            padrao_formatado = f"0:{partes[0]} | 1:{partes[1]} | 2:{partes[2]} | 3:{partes[3]}"

            # Verificar se é igual ao padrão campeão
            apareceu = (padrao_formatado == padrao_campea_original)

            timeline.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'apareceu': apareceu,
                'numeros': sorted(numeros_sorteio),
                'padrao': padrao_formatado
            })

        return timeline

    @staticmethod
    def _extrair_padrao_visual(padrao_descricao):
        """
        Converte padrão do formato "0:2 | 1:3 | 2:2 | 3:0" para "0 0 1 1 1 2 2"
        """
        if not padrao_descricao:
            return ""

        partes = padrao_descricao.split(' | ')
        digitos = []

        for parte in partes:
            if ':' in parte:
                digito, qtd = parte.split(':')
                for _ in range(int(qtd)):
                    digitos.append(digito)

        return ' '.join(digitos)

    # =========================================================================
    # NOVA FUNCIONALIDADE: ANÁLISE DE PADRÕES POR DEZENAS (ATUALIZADA)
    # =========================================================================

    @staticmethod
    def calcular_padroes_possiveis():
        """
        Calcula TODOS os padrões possíveis de dezenas para 7 números do Dia de Sorte.

        Mapeamento:
        - Faixa 0: 01-09 (9 números)
        - Faixa 1: 10-19 (10 números)
        - Faixa 2: 20-29 (10 números)
        - Faixa 3: 30-31 (2 números)

        Returns:
            Lista de padrões possíveis com quantidade de jogos que cada um pode gerar
        """
        # Limites de cada faixa
        limites = {
            0: 9,   # 01-09
            1: 10,  # 10-19
            2: 10,  # 20-29
            3: 2    # 30-31
        }

        padroes_possiveis = []
        padroes_teoricos_count = 0  # Contador de padrões teóricos (sem restrição)

        # Gerar todas as combinações possíveis onde a soma = 7
        # Cada padrão é (qtd_faixa0, qtd_faixa1, qtd_faixa2, qtd_faixa3)
        for f0 in range(8):  # 0 a 7
            for f1 in range(8 - f0):
                for f2 in range(8 - f0 - f1):
                    f3 = 7 - f0 - f1 - f2

                    if f3 >= 0:
                        padroes_teoricos_count += 1

                        # Verificar se é VIÁVEL (respeita os limites das faixas)
                        if f0 <= limites[0] and f1 <= limites[1] and f2 <= limites[2] and f3 <= limites[3]:
                            # Calcular quantos jogos este padrão pode gerar
                            # Usando combinação: C(n, k) para cada faixa
                            jogos_possiveis = 1

                            if f0 > 0:
                                jogos_possiveis *= comb(limites[0], f0)
                            if f1 > 0:
                                jogos_possiveis *= comb(limites[1], f1)
                            if f2 > 0:
                                jogos_possiveis *= comb(limites[2], f2)
                            if f3 > 0:
                                jogos_possiveis *= comb(limites[3], f3)

                            # Criar representação visual do padrão
                            padrao_visual = []
                            for _ in range(f0): padrao_visual.append('0')
                            for _ in range(f1): padrao_visual.append('1')
                            for _ in range(f2): padrao_visual.append('2')
                            for _ in range(f3): padrao_visual.append('3')

                            padroes_possiveis.append({
                                'padrao': ' '.join(padrao_visual),
                                'distribuicao': f"{f0}-{f1}-{f2}-{f3}",
                                'descricao': f"0:{f0} | 1:{f1} | 2:{f2} | 3:{f3}",
                                'faixa_0': f0,
                                'faixa_1': f1,
                                'faixa_2': f2,
                                'faixa_3': f3,
                                'jogos_possiveis': jogos_possiveis,
                                'percentual_universo': 0  # Será calculado depois
                            })

        # Calcular total de jogos possíveis (C(31,7) = 2.629.575)
        total_jogos_universo = comb(31, 7)

        # Calcular percentual de cada padrão no universo
        for padrao in padroes_possiveis:
            padrao['percentual_universo'] = round(
                (padrao['jogos_possiveis'] / total_jogos_universo) * 100, 4
            )

        # Ordenar por quantidade de jogos possíveis (decrescente)
        padroes_possiveis.sort(key=lambda x: x['jogos_possiveis'], reverse=True)

        return {
            'padroes': padroes_possiveis,
            'total_padroes_teoricos': padroes_teoricos_count,  # 120 (sem restrições)
            'total_padroes_viaveis': len(padroes_possiveis),   # Com restrições
            'total_jogos_universo': total_jogos_universo
        }

    @staticmethod
    def analisar_padroes_dezenas():
        """
        Análise COMPLETA de padrões por dezenas:
        - Todos os padrões possíveis (teóricos vs viáveis)
        - Padrões que já saíram (frequência histórica) - TODOS, não apenas top 10
        - Padrões que NUNCA saíram (FALTANTES) - TODOS
        - Ranking
        - Insights
        - Recomendações

        Returns:
            Dicionário completo com toda a análise
        """
        # 1. Calcular padrões possíveis
        dados_possiveis = AnaliseDigitoPadraoInicialFinalService.calcular_padroes_possiveis()
        padroes_possiveis = dados_possiveis['padroes']

        # 2. Buscar todos os sorteios
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        # 3. Analisar cada sorteio e contar padrões
        padroes_encontrados = defaultdict(list)  # padrao -> lista de concursos

        for sorteio in sorteios:
            numeros = []
            for pos in range(1, 8):
                numero = getattr(sorteio, f'posicao_{pos}')
                if numero:
                    numeros.append(numero)

            if len(numeros) == 7:
                # Classificar cada número em sua faixa
                faixas = []
                for num in sorted(numeros):
                    if num <= 9:
                        faixas.append('0')
                    elif num <= 19:
                        faixas.append('1')
                    elif num <= 29:
                        faixas.append('2')
                    else:
                        faixas.append('3')

                padrao = ' '.join(faixas)

                padroes_encontrados[padrao].append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': sorted(numeros)
                })

        # 4. Classificar padrões: já saíram vs faltantes
        padroes_que_sairam = []
        padroes_faltantes = []

        for padrao_info in padroes_possiveis:
            padrao = padrao_info['padrao']
            concursos = padroes_encontrados.get(padrao, [])
            frequencia = len(concursos)

            # Calcular atraso (para padrões que já saíram)
            if frequencia > 0:
                ultimo_apareceu = concursos[0]['concurso']  # Lista já ordenada desc
                atraso = ultimo_concurso - ultimo_apareceu
            else:
                atraso = total_concursos  # Nunca saiu

            dado_padrao = {
                'padrao': padrao,
                'distribuicao': padrao_info['distribuicao'],
                'descricao': padrao_info['descricao'],
                'faixa_0': padrao_info['faixa_0'],
                'faixa_1': padrao_info['faixa_1'],
                'faixa_2': padrao_info['faixa_2'],
                'faixa_3': padrao_info['faixa_3'],
                'jogos_possiveis': padrao_info['jogos_possiveis'],
                'percentual_universo': padrao_info['percentual_universo'],
                'frequencia': frequencia,
                'percentual_historico': round((frequencia / total_concursos) * 100, 2) if frequencia > 0 else 0,
                'atraso': atraso,
                'ultimo_concurso': concursos[0]['concurso'] if concursos else None,
                'concursos': concursos[:10]  # Últimos 10 para não sobrecarregar
            }

            if frequencia > 0:
                padroes_que_sairam.append(dado_padrao)
            else:
                padroes_faltantes.append(dado_padrao)

        # 5. Ordenar padrões
        padroes_que_sairam.sort(key=lambda x: x['frequencia'], reverse=True)
        padroes_faltantes.sort(key=lambda x: x['jogos_possiveis'], reverse=True)

        # 6. Gerar Insights Inteligentes
        insights = AnaliseDigitoPadraoInicialFinalService._gerar_insights_dezenas(
            padroes_que_sairam, padroes_faltantes, total_concursos
        )

        # 7. Gerar Recomendações Estratégicas
        recomendacoes = AnaliseDigitoPadraoInicialFinalService._gerar_recomendacoes_dezenas(
            padroes_que_sairam, padroes_faltantes
        )

        return {
            'sucesso': True,
            'total_concursos': total_concursos,
            'ultimo_concurso': ultimo_concurso,

            # =============================================
            # 🆕 NOVOS CAMPOS: Totais detalhados
            # =============================================
            'total_padroes_teoricos': dados_possiveis['total_padroes_teoricos'],  # 120
            'total_padroes_viaveis': dados_possiveis['total_padroes_viaveis'],    # Padrões que respeitam limites
            'total_padroes_possiveis': len(padroes_possiveis),  # Mantido para compatibilidade
            'total_padroes_que_sairam': len(padroes_que_sairam),
            'total_padroes_faltantes': len(padroes_faltantes),
            'total_jogos_universo': dados_possiveis['total_jogos_universo'],

            # =============================================
            # 🆕 TODOS OS PADRÕES (não apenas top 10)
            # =============================================
            'todos_padroes_que_sairam': padroes_que_sairam,  # TODOS ordenados por frequência
            'todos_padroes_faltantes': padroes_faltantes,    # TODOS ordenados por jogos_possiveis

            # Top 10 para exibição rápida (mantido para compatibilidade)
            'padroes_que_sairam': padroes_que_sairam,  # Alias
            'padroes_faltantes': padroes_faltantes,    # Alias
            'top_10_frequentes': padroes_que_sairam[:10],
            'top_10_atrasados': sorted(padroes_que_sairam, key=lambda x: x['atraso'], reverse=True)[:10],

            # =============================================
            # 🆕 TODOS ordenados por atraso
            # =============================================
            'todos_por_atraso': sorted(padroes_que_sairam, key=lambda x: x['atraso'], reverse=True),

            'insights': insights,
            'recomendacoes': recomendacoes
        }

    @staticmethod
    def _gerar_insights_dezenas(padroes_que_sairam, padroes_faltantes, total_concursos):
        """Gera insights inteligentes sobre os padrões de dezenas"""
        insights = []

        # Insight 1: Padrão Campeão
        if padroes_que_sairam:
            campeao = padroes_que_sairam[0]
            insights.append({
                'icone': '👑',
                'titulo': 'Padrão Campeão',
                'texto': f"O padrão <strong>{campeao['padrao']}</strong> é o mais frequente com {campeao['frequencia']} ocorrências ({campeao['percentual_historico']}%)",
                'cor': 'success'
            })

        # Insight 2: Padrões Faltantes
        if padroes_faltantes:
            insights.append({
                'icone': '🎯',
                'titulo': 'Padrões que Nunca Saíram',
                'texto': f"Existem <strong>{len(padroes_faltantes)} padrões</strong> que NUNCA apareceram nos {total_concursos} concursos!",
                'cor': 'danger'
            })

            # Listar os 3 faltantes com mais jogos possíveis
            top_faltantes = padroes_faltantes[:3]
            if top_faltantes:
                lista = ', '.join([f"'{p['padrao']}' ({p['jogos_possiveis']:,} jogos)" for p in top_faltantes])
                insights.append({
                    'icone': '💡',
                    'titulo': 'Faltantes com Maior Potencial',
                    'texto': f"Padrões faltantes com mais combinações possíveis: {lista}",
                    'cor': 'warning'
                })

        # Insight 3: Concentração
        if padroes_que_sairam:
            # Top 3 representam quanto do total?
            top3_freq = sum(p['frequencia'] for p in padroes_que_sairam[:3])
            percentual_top3 = round((top3_freq / total_concursos) * 100, 1)

            insights.append({
                'icone': '📊',
                'titulo': 'Concentração nos Top 3',
                'texto': f"Os 3 padrões mais frequentes representam <strong>{percentual_top3}%</strong> de todos os sorteios",
                'cor': 'info'
            })

        # Insight 4: Padrão mais atrasado
        if padroes_que_sairam:
            mais_atrasado = max(padroes_que_sairam, key=lambda x: x['atraso'])
            if mais_atrasado['atraso'] > 50:
                insights.append({
                    'icone': '⏰',
                    'titulo': 'Padrão Mais Atrasado',
                    'texto': f"O padrão <strong>{mais_atrasado['padrao']}</strong> está há {mais_atrasado['atraso']} concursos sem sair!",
                    'cor': 'warning'
                })

        # Insight 5: Equilíbrio
        equilibrados = [p for p in padroes_que_sairam if p['faixa_0'] >= 1 and p['faixa_1'] >= 1 and p['faixa_2'] >= 1]
        freq_equilibrados = sum(p['frequencia'] for p in equilibrados)
        perc_equilibrados = round((freq_equilibrados / total_concursos) * 100, 1)

        insights.append({
            'icone': '⚖️',
            'titulo': 'Padrões Equilibrados',
            'texto': f"Padrões com números em pelo menos 3 faixas representam <strong>{perc_equilibrados}%</strong> dos sorteios",
            'cor': 'primary'
        })

        return insights

    @staticmethod
    def _gerar_recomendacoes_dezenas(padroes_que_sairam, padroes_faltantes):
        """Gera recomendações estratégicas baseadas na análise"""
        recomendacoes = []

        # Recomendação 1: Apostar nos mais frequentes
        if padroes_que_sairam:
            top3 = padroes_que_sairam[:3]
            padroes_str = ', '.join([f"'{p['padrao']}'" for p in top3])
            recomendacoes.append({
                'icone': '✅',
                'titulo': 'Aposte nos Padrões Quentes',
                'texto': f"Priorize os padrões mais frequentes: {padroes_str}",
                'tipo': 'sucesso'
            })

        # Recomendação 2: Padrões atrasados
        atrasados = sorted(padroes_que_sairam, key=lambda x: x['atraso'], reverse=True)[:3]
        if atrasados and atrasados[0]['atraso'] > 30:
            padroes_str = ', '.join([f"'{p['padrao']}' ({p['atraso']} conc.)" for p in atrasados])
            recomendacoes.append({
                'icone': '🎲',
                'titulo': 'Considere Padrões Atrasados',
                'texto': f'Estes padrões estão "devidos": {padroes_str}',
                'tipo': 'alerta'
            })

        # Recomendação 3: Evitar padrões extremos
        extremos_faltantes = [p for p in padroes_faltantes if (p['faixa_3'] >= 2 or p['faixa_0'] >= 6)]
        if extremos_faltantes:
            recomendacoes.append({
                'icone': '⚠️',
                'titulo': 'Evite Padrões Extremos',
                'texto': f"Padrões com muitos números na faixa 30-31 ou só na faixa 01-09 são muito raros",
                'tipo': 'perigo'
            })

        # Recomendação 4: Padrão equilibrado ideal
        recomendacoes.append({
            'icone': '💡',
            'titulo': 'Distribuição Ideal',
            'texto': "O padrão ideal tem 1-2 números na faixa 0, 2-3 na faixa 1, 2-3 na faixa 2, e 0-1 na faixa 3",
            'tipo': 'info'
        })

        # Recomendação 5: Padrões faltantes com chance
        faltantes_viaveis = [p for p in padroes_faltantes if p['jogos_possiveis'] > 1000]
        if faltantes_viaveis:
            recomendacoes.append({
                'icone': '🎯',
                'titulo': 'Faltantes Viáveis para Arriscar',
                'texto': f"Existem {len(faltantes_viaveis)} padrões que nunca saíram mas têm boa quantidade de combinações possíveis",
                'tipo': 'especial'
            })

        return recomendacoes
