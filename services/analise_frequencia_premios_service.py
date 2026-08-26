"""
Service para Análise de Frequência de Prêmios - Dia de Sorte
Analisa padrões estatísticos dos concursos com 7 acertos
"""

from collections import Counter, defaultdict
from models import Sorteio


class AnaliseFrequenciaPremiosService:

    @staticmethod
    def obter_analise_completa():
        """Obtém análise completa dos sorteios premiados"""
        sorteios_premiados = Sorteio.query.filter(Sorteio.ganhadores_7_acertos > 0).order_by(Sorteio.concurso.asc()).all()

        if not sorteios_premiados:
            return {
                'erro': 'Nenhum sorteio com prêmio principal encontrado',
                'total_premios': 0
            }

        # Calcular total de sorteios e diferença
        total_sorteios = Sorteio.query.count()
        total_premios = len(sorteios_premiados)
        diferenca_sorteios_premios = total_sorteios - total_premios

        # Gerar insights inteligentes
        insights = AnaliseFrequenciaPremiosService.gerar_insights_inteligentes(sorteios_premiados)

        return {
            'total_premios': total_premios,
            'total_sorteios': total_sorteios,
            'diferenca_sorteios_premios': diferenca_sorteios_premios,
            'total_ganhadores': sum(s.ganhadores_7_acertos for s in sorteios_premiados),
            'valor_total_pago': sum(s.valor_premio_7_acertos * s.ganhadores_7_acertos for s in sorteios_premiados),

            # Insights Inteligentes
            'insights': insights,

            # Resumo Consolidado (Tabela)
            'resumo_tabela': AnaliseFrequenciaPremiosService.gerar_resumo_tabela(sorteios_premiados),

            # Top 3 - Dezenas mais frequentes
            'top_dezenas': AnaliseFrequenciaPremiosService.analisar_dezenas_premiadas(sorteios_premiados)[:3],

            # Top 3 - Padrões dominantes
            'top_padroes_pares_impares': AnaliseFrequenciaPremiosService.analisar_pares_impares_premiados(sorteios_premiados)[:3],
            'top_padroes_digitos_finais': AnaliseFrequenciaPremiosService.analisar_digitos_finais(sorteios_premiados)[:3],
            'top_padroes_quadrantes': AnaliseFrequenciaPremiosService.analisar_quadrantes(sorteios_premiados)[:3],
            'top_consecutivos': AnaliseFrequenciaPremiosService.analisar_consecutivos(sorteios_premiados)[:3],
            'top_repeticoes': AnaliseFrequenciaPremiosService.analisar_repeticoes(sorteios_premiados)[:3],
            'top_meses': AnaliseFrequenciaPremiosService.analisar_meses_premiados(sorteios_premiados)[:3],

            # Top 3 - Atrasos
            'top_atrasos': AnaliseFrequenciaPremiosService.analisar_atrasos(sorteios_premiados)[:3],

            # Top 3 - Sequências
            'top_sequencias': AnaliseFrequenciaPremiosService.analisar_sequencias(sorteios_premiados)[:3],

            # Top 3 - GAPS (Distâncias entre dezenas)
            'top_gaps': AnaliseFrequenciaPremiosService.analisar_gaps(sorteios_premiados)[:3],

            # Top 3 - Padrões de dígitos iniciais
            'top_padroes_digitos_iniciais': AnaliseFrequenciaPremiosService.analisar_padroes_digitos_iniciais(sorteios_premiados)[:3],

            # Correlação mês x dezena
            'correlacao_mes_dezena': AnaliseFrequenciaPremiosService.analisar_correlacao_mes_dezena(sorteios_premiados)[:10],

            # Dados completos (para tabelas detalhadas)
            'dezenas_completas': AnaliseFrequenciaPremiosService.analisar_dezenas_premiadas(sorteios_premiados),
            'meses_completos': AnaliseFrequenciaPremiosService.analisar_meses_premiados(sorteios_premiados),
            'padroes_completos': AnaliseFrequenciaPremiosService.analisar_pares_impares_premiados(sorteios_premiados),

            # Jogos Vencedores Detalhados
            'jogos_vencedores': AnaliseFrequenciaPremiosService.obter_jogos_vencedores_detalhados(sorteios_premiados),
            'analise_repeticoes_entre_premios': AnaliseFrequenciaPremiosService.analisar_repeticoes_entre_premios(sorteios_premiados),
            'matriz_comparacao_dezenas': AnaliseFrequenciaPremiosService.gerar_matriz_comparacao_dezenas(sorteios_premiados),

            # Análise de Números Altos (posicao_1 >= 10)
            'analise_numeros_altos': AnaliseFrequenciaPremiosService.analisar_numeros_altos()
        }

    @staticmethod
    def analisar_dezenas_premiadas(sorteios):
        """Analisa frequência de dezenas nos sorteios premiados"""
        contador_dezenas = Counter()

        for sorteio in sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            contador_dezenas.update(numeros)

        total_sorteios = len(sorteios)
        resultado = []

        for dezena, freq in contador_dezenas.most_common(31):
            resultado.append({
                'dezena': dezena,
                'frequencia': freq,
                'percentual': round((freq / total_sorteios) * 100, 2),
                'aparicoes_total': freq,
                'media_aparicoes': round(freq / total_sorteios, 2)
            })

        return resultado

    @staticmethod
    def analisar_meses_premiados(sorteios):
        """Analisa frequência de meses nos sorteios premiados"""
        contador_meses = Counter()

        for sorteio in sorteios:
            contador_meses[sorteio.mes_sorte] += 1

        total_sorteios = len(sorteios)
        resultado = []

        for mes, freq in contador_meses.most_common(12):
            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseFrequenciaPremiosService.obter_nome_mes(mes),
                'frequencia': freq,
                'percentual': round((freq / total_sorteios) * 100, 2),
                'ganhadores_total': sum(s.ganhadores_7_acertos for s in sorteios if s.mes_sorte == mes)
            })

        return resultado

    @staticmethod
    def analisar_pares_impares_premiados(sorteios):
        """Analisa padrões de pares e ímpares"""
        contador_padroes = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 7 - pares
            padrao = f"{pares}P + {impares}I"

            contador_padroes[padrao]['frequencia'] += 1
            if len(contador_padroes[padrao]['exemplos']) < 3:
                contador_padroes[padrao]['exemplos'].append(sorteio.concurso)

        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_padroes.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_digitos_finais(sorteios):
        """Analisa padrões de dígitos finais (0-9)"""
        contador_digitos = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            # Contar dígitos finais
            digitos = [n % 10 for n in numeros]
            digitos_unicos = len(set(digitos))

            padrao = f"{digitos_unicos} dígitos únicos"

            contador_digitos[padrao]['frequencia'] += 1
            if len(contador_digitos[padrao]['exemplos']) < 3:
                contador_digitos[padrao]['exemplos'].append(sorteio.concurso)

        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_digitos.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_quadrantes(sorteios):
        """Analisa distribuição por quadrantes (1-7, 8-15, 16-23, 24-31)"""
        contador_quadrantes = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            q1 = sum(1 for n in numeros if 1 <= n <= 7)
            q2 = sum(1 for n in numeros if 8 <= n <= 15)
            q3 = sum(1 for n in numeros if 16 <= n <= 23)
            q4 = sum(1 for n in numeros if 24 <= n <= 31)

            padrao = f"Q1:{q1} Q2:{q2} Q3:{q3} Q4:{q4}"

            contador_quadrantes[padrao]['frequencia'] += 1
            if len(contador_quadrantes[padrao]['exemplos']) < 3:
                contador_quadrantes[padrao]['exemplos'].append(sorteio.concurso)

        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_quadrantes.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_consecutivos(sorteios):
        """Analisa quantidade de números consecutivos"""
        contador_consecutivos = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Contar consecutivos
            consecutivos = 0
            for i in range(len(numeros) - 1):
                if numeros[i + 1] == numeros[i] + 1:
                    consecutivos += 1

            padrao = f"{consecutivos} consecutivos"

            contador_consecutivos[padrao]['frequencia'] += 1
            if len(contador_consecutivos[padrao]['exemplos']) < 3:
                contador_consecutivos[padrao]['exemplos'].append(sorteio.concurso)

        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_consecutivos.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_repeticoes(sorteios):
        """Analisa repetições de números do concurso anterior"""
        if len(sorteios) < 2:
            return []

        contador_repeticoes = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for i in range(1, len(sorteios)):
            sorteio_atual = sorteios[i]
            sorteio_anterior = sorteios[i - 1]

            numeros_atual = set([
                sorteio_atual.posicao_1, sorteio_atual.posicao_2, sorteio_atual.posicao_3,
                sorteio_atual.posicao_4, sorteio_atual.posicao_5, sorteio_atual.posicao_6,
                sorteio_atual.posicao_7
            ])

            numeros_anterior = set([
                sorteio_anterior.posicao_1, sorteio_anterior.posicao_2, sorteio_anterior.posicao_3,
                sorteio_anterior.posicao_4, sorteio_anterior.posicao_5, sorteio_anterior.posicao_6,
                sorteio_anterior.posicao_7
            ])

            repeticoes = len(numeros_atual & numeros_anterior)
            padrao = f"{repeticoes} repetições"

            contador_repeticoes[padrao]['frequencia'] += 1
            if len(contador_repeticoes[padrao]['exemplos']) < 3:
                contador_repeticoes[padrao]['exemplos'].append(sorteio_atual.concurso)

        total = len(sorteios) - 1
        resultado = []

        for padrao, dados in sorted(contador_repeticoes.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_atrasos(sorteios):
        """Analisa dezenas com maiores atrasos nos sorteios premiados"""
        # Obter todos os sorteios (não só premiados) para calcular atraso real
        todos_sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not todos_sorteios:
            return []

        # Última aparição de cada dezena
        ultima_aparicao = {}

        for sorteio in reversed(todos_sorteios):
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            for num in numeros:
                if num not in ultima_aparicao:
                    ultima_aparicao[num] = sorteio.concurso

        ultimo_concurso = todos_sorteios[0].concurso
        atrasos = []

        for dezena in range(1, 32):
            if dezena in ultima_aparicao:
                atraso = ultimo_concurso - ultima_aparicao[dezena]
                atrasos.append({
                    'dezena': dezena,
                    'atraso': atraso,
                    'ultimo_concurso': ultima_aparicao[dezena]
                })

        return sorted(atrasos, key=lambda x: x['atraso'], reverse=True)

    @staticmethod
    def analisar_sequencias(sorteios):
        """Analisa maiores sequências encontradas nos sorteios premiados"""
        sequencias_encontradas = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Encontrar sequências
            sequencias = []
            seq_atual = [numeros[0]]

            for i in range(1, len(numeros)):
                if numeros[i] == seq_atual[-1] + 1:
                    seq_atual.append(numeros[i])
                else:
                    if len(seq_atual) >= 2:
                        sequencias.append(seq_atual[:])
                    seq_atual = [numeros[i]]

            if len(seq_atual) >= 2:
                sequencias.append(seq_atual)

            # Contar padrão
            if sequencias:
                maior_seq = max(sequencias, key=len)
                padrao = f"Seq de {len(maior_seq)}: {'-'.join(map(str, maior_seq))}"

                sequencias_encontradas[padrao]['frequencia'] += 1
                if len(sequencias_encontradas[padrao]['exemplos']) < 3:
                    sequencias_encontradas[padrao]['exemplos'].append(sorteio.concurso)

        resultado = []
        for padrao, dados in sorted(sequencias_encontradas.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_correlacao_mes_dezena(sorteios):
        """Analisa correlação entre mês e dezenas mais sorteadas"""
        correlacoes = defaultdict(lambda: defaultdict(int))

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            for num in numeros:
                correlacoes[mes][num] += 1

        # Encontrar top correlações
        resultado = []
        for mes, dezenas in correlacoes.items():
            for dezena, freq in sorted(dezenas.items(), key=lambda x: x[1], reverse=True)[:3]:
                resultado.append({
                    'mes': mes,
                    'mes_nome': AnaliseFrequenciaPremiosService.obter_nome_mes(mes),
                    'dezena': dezena,
                    'frequencia': freq
                })

        # Ordenar por frequência e retornar top
        return sorted(resultado, key=lambda x: x['frequencia'], reverse=True)

    @staticmethod
    def analisar_gaps(sorteios):
        """
        Analisa os gaps (distâncias) entre as dezenas sorteadas
        Exemplo: [02, 08, 15, 23, 27, 29, 31] -> gaps: [6, 7, 8, 4, 2, 2]
        """
        contador_padroes = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Calcular gaps (distâncias entre números consecutivos)
            gaps = []
            for i in range(len(numeros) - 1):
                gap = numeros[i + 1] - numeros[i]
                gaps.append(gap)

            # Criar padrão como string
            padrao = ' '.join(map(str, gaps))

            # Armazenar
            contador_padroes[padrao]['frequencia'] += 1
            if len(contador_padroes[padrao]['exemplos']) < 3:
                contador_padroes[padrao]['exemplos'].append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros,
                    'gaps': gaps
                })

        # Formatar resultado
        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_padroes.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def analisar_padroes_digitos_iniciais(sorteios):
        """
        Analisa padrões de dígitos iniciais das dezenas sorteadas
        Exemplo: [04, 08, 12, 17, 24, 27, 29] -> "0 0 1 1 2 2 2"
        """
        contador_padroes = defaultdict(lambda: {'frequencia': 0, 'exemplos': []})

        for sorteio in sorteios:
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Extrair dígito inicial de cada número (04 -> 0, 12 -> 1, 24 -> 2)
            digitos_iniciais = []
            for num in numeros:
                # Para números 1-9, dígito inicial é 0
                # Para números 10-19, dígito inicial é 1
                # Para números 20-29, dígito inicial é 2
                # Para números 30-31, dígito inicial é 3
                if num < 10:
                    digitos_iniciais.append(0)
                else:
                    digitos_iniciais.append(num // 10)

            # Criar padrão como string
            padrao = ' '.join(map(str, digitos_iniciais))

            # Armazenar
            contador_padroes[padrao]['frequencia'] += 1
            if len(contador_padroes[padrao]['exemplos']) < 3:
                contador_padroes[padrao]['exemplos'].append({
                    'concurso': sorteio.concurso,
                    'numeros': numeros
                })

        # Formatar resultado
        total = len(sorteios)
        resultado = []

        for padrao, dados in sorted(contador_padroes.items(), key=lambda x: x[1]['frequencia'], reverse=True):
            resultado.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': round((dados['frequencia'] / total) * 100, 2),
                'exemplos': dados['exemplos']
            })

        return resultado

    @staticmethod
    def obter_ultimos_premiados(sorteios, limite=10):
        """Obtém últimos sorteios premiados"""
        ultimos = sorted(sorteios, key=lambda x: x.concurso, reverse=True)[:limite]
        resultado = []

        for sorteio in ultimos:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            resultado.append({
                'concurso': sorteio.concurso,
                'numeros': sorted(numeros),
                'mes_sorte': sorteio.mes_sorte,
                'mes_nome': sorteio.get_nome_mes(),
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'ganhadores': sorteio.ganhadores_7_acertos,
                'valor_premio': sorteio.valor_premio_7_acertos
            })

        return resultado

    @staticmethod
    def gerar_insights_inteligentes(sorteios):
        """Gera insights inteligentes baseados nos dados"""
        insights = []

        # Análise de dezenas
        dezenas = AnaliseFrequenciaPremiosService.analisar_dezenas_premiadas(sorteios)
        if dezenas:
            top_dezena = dezenas[0]
            insights.append({
                'tipo': 'dezena',
                'titulo': 'Dezena Campeã',
                'descricao': f"A dezena {top_dezena['dezena']} é a mais sorteada nos prêmios, aparecendo {top_dezena['frequencia']} vezes ({top_dezena['percentual']}%).",
                'icone': 'star',
                'cor': 'success'
            })

        # Análise de pares/ímpares
        pares_impares = AnaliseFrequenciaPremiosService.analisar_pares_impares_premiados(sorteios)
        if pares_impares:
            top_padrao = pares_impares[0]
            insights.append({
                'tipo': 'padrao',
                'titulo': 'Padrão Dominante',
                'descricao': f"O padrão '{top_padrao['padrao']}' é o mais comum, ocorrendo em {top_padrao['percentual']}% dos prêmios.",
                'icone': 'balance-scale',
                'cor': 'info'
            })

        # Análise de meses
        meses = AnaliseFrequenciaPremiosService.analisar_meses_premiados(sorteios)
        if meses:
            top_mes = meses[0]
            bottom_mes = meses[-1]
            insights.append({
                'tipo': 'mes',
                'titulo': 'Mês da Sorte',
                'descricao': f"{top_mes['mes_nome']} teve {top_mes['frequencia']} prêmios ({top_mes['percentual']}%), enquanto {bottom_mes['mes_nome']} teve apenas {bottom_mes['frequencia']}.",
                'icone': 'calendar-check',
                'cor': 'warning'
            })

        # Análise de consecutivos
        consecutivos = AnaliseFrequenciaPremiosService.analisar_consecutivos(sorteios)
        if consecutivos:
            top_consecutivo = consecutivos[0]
            insights.append({
                'tipo': 'consecutivo',
                'titulo': 'Números Consecutivos',
                'descricao': f"O padrão '{top_consecutivo['padrao']}' aparece em {top_consecutivo['percentual']}% dos sorteios premiados.",
                'icone': 'link',
                'cor': 'primary'
            })

        # Análise de repetições
        repeticoes = AnaliseFrequenciaPremiosService.analisar_repeticoes(sorteios)
        if repeticoes:
            top_repeticao = repeticoes[0]
            insights.append({
                'tipo': 'repeticao',
                'titulo': 'Repetições do Concurso Anterior',
                'descricao': f"{top_repeticao['padrao']} do concurso anterior é o mais comum ({top_repeticao['percentual']}%).",
                'icone': 'redo',
                'cor': 'secondary'
            })

        # Análise de tendência recente
        ultimos_5 = sorteios[-5:] if len(sorteios) >= 5 else sorteios
        contador_recente = Counter()
        for sorteio in ultimos_5:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            contador_recente.update(numeros)

        if contador_recente:
            dezena_quente = contador_recente.most_common(1)[0]
            insights.append({
                'tipo': 'tendencia',
                'titulo': 'Tendência Recente',
                'descricao': f"Nos últimos {len(ultimos_5)} prêmios, a dezena {dezena_quente[0]} apareceu {dezena_quente[1]} vezes.",
                'icone': 'fire',
                'cor': 'danger'
            })

        return insights

    @staticmethod
    def gerar_resumo_tabela(sorteios):
        """Gera resumo consolidado em formato de tabela"""
        # Análises necessárias
        dezenas = AnaliseFrequenciaPremiosService.analisar_dezenas_premiadas(sorteios)
        pares_impares = AnaliseFrequenciaPremiosService.analisar_pares_impares_premiados(sorteios)
        meses = AnaliseFrequenciaPremiosService.analisar_meses_premiados(sorteios)
        consecutivos = AnaliseFrequenciaPremiosService.analisar_consecutivos(sorteios)
        repeticoes = AnaliseFrequenciaPremiosService.analisar_repeticoes(sorteios)
        quadrantes = AnaliseFrequenciaPremiosService.analisar_quadrantes(sorteios)

        # Calcular médias
        total_sorteios = len(sorteios)
        todas_dezenas = []
        for sorteio in sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            todas_dezenas.extend(numeros)

        media_soma = sum(todas_dezenas) / total_sorteios if total_sorteios > 0 else 0
        media_pares = sum(1 for n in todas_dezenas if n % 2 == 0) / total_sorteios if total_sorteios > 0 else 0

        resumo = [
            {
                'categoria': 'Dezenas',
                'mais_frequente': f"{dezenas[0]['dezena']} ({dezenas[0]['frequencia']}x)" if dezenas else '-',
                'menos_frequente': f"{dezenas[-1]['dezena']} ({dezenas[-1]['frequencia']}x)" if len(dezenas) > 1 else '-',
                'observacao': f"{dezenas[0]['percentual']}% de aparição" if dezenas else '-'
            },
            {
                'categoria': 'Pares/Ímpares',
                'mais_frequente': pares_impares[0]['padrao'] if pares_impares else '-',
                'menos_frequente': pares_impares[-1]['padrao'] if len(pares_impares) > 1 else '-',
                'observacao': f"{pares_impares[0]['percentual']}% dos prêmios" if pares_impares else '-'
            },
            {
                'categoria': 'Meses',
                'mais_frequente': f"{meses[0]['mes_nome']} ({meses[0]['frequencia']}x)" if meses else '-',
                'menos_frequente': f"{meses[-1]['mes_nome']} ({meses[-1]['frequencia']}x)" if len(meses) > 1 else '-',
                'observacao': f"{meses[0]['percentual']}% de ocorrência" if meses else '-'
            },
            {
                'categoria': 'Consecutivos',
                'mais_frequente': consecutivos[0]['padrao'] if consecutivos else '-',
                'menos_frequente': consecutivos[-1]['padrao'] if len(consecutivos) > 1 else '-',
                'observacao': f"{consecutivos[0]['percentual']}% de frequência" if consecutivos else '-'
            },
            {
                'categoria': 'Repetições',
                'mais_frequente': repeticoes[0]['padrao'] if repeticoes else '-',
                'menos_frequente': repeticoes[-1]['padrao'] if len(repeticoes) > 1 else '-',
                'observacao': f"{repeticoes[0]['percentual']}% dos casos" if repeticoes else '-'
            },
            {
                'categoria': 'Quadrantes',
                'mais_frequente': quadrantes[0]['padrao'] if quadrantes else '-',
                'menos_frequente': quadrantes[-1]['padrao'] if len(quadrantes) > 1 else '-',
                'observacao': f"{quadrantes[0]['percentual']}% de ocorrência" if quadrantes else '-'
            },
            {
                'categoria': 'Médias Gerais',
                'mais_frequente': f"Soma: {media_soma:.1f}",
                'menos_frequente': f"Pares: {media_pares:.1f}",
                'observacao': f"Base: {total_sorteios} prêmios"
            }
        ]

        return resumo

    @staticmethod
    def obter_jogos_vencedores_detalhados(sorteios):
        """Obtém lista completa de jogos vencedores com detalhes"""
        jogos = []

        for i, sorteio in enumerate(sorteios):
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Calcular intervalo desde o último prêmio
            intervalo = None
            if i > 0:
                concurso_anterior = sorteios[i - 1].concurso
                intervalo = sorteio.concurso - concurso_anterior

            # Verificar repetições com o jogo anterior
            repeticoes_anterior = 0
            dezenas_repetidas = []
            if i > 0:
                numeros_anterior = set([
                    sorteios[i-1].posicao_1, sorteios[i-1].posicao_2, sorteios[i-1].posicao_3,
                    sorteios[i-1].posicao_4, sorteios[i-1].posicao_5, sorteios[i-1].posicao_6,
                    sorteios[i-1].posicao_7
                ])
                numeros_atual = set(numeros)
                dezenas_repetidas = sorted(list(numeros_atual & numeros_anterior))
                repeticoes_anterior = len(dezenas_repetidas)

            # Análise do jogo
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 7 - pares
            soma = sum(numeros)

            # Consecutivos
            consecutivos = 0
            for j in range(len(numeros) - 1):
                if numeros[j + 1] == numeros[j] + 1:
                    consecutivos += 1

            jogos.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '-',
                'data_completa': sorteio.data_sorteio.strftime('%d/%m/%Y %H:%M') if sorteio.data_sorteio else '-',
                'numeros': numeros,
                'mes_sorte': sorteio.mes_sorte,
                'mes_nome': AnaliseFrequenciaPremiosService.obter_nome_mes(sorteio.mes_sorte),
                'ganhadores': sorteio.ganhadores_7_acertos,
                'valor_premio': sorteio.valor_premio_7_acertos,
                'intervalo': intervalo,
                'repeticoes_anterior': repeticoes_anterior,
                'dezenas_repetidas': dezenas_repetidas,
                'pares': pares,
                'impares': impares,
                'soma': soma,
                'consecutivos': consecutivos,
                'sequencia_numero': i + 1
            })

        return jogos

    @staticmethod
    def analisar_repeticoes_entre_premios(sorteios):
        """Analisa padrões de repetições entre jogos premiados consecutivos"""
        if len(sorteios) < 2:
            return {
                'total_comparacoes': 0,
                'estatisticas': {},
                'detalhes': []
            }

        contador_repeticoes = Counter()
        detalhes = []

        for i in range(1, len(sorteios)):
            sorteio_atual = sorteios[i]
            sorteio_anterior = sorteios[i - 1]

            numeros_atual = set([
                sorteio_atual.posicao_1, sorteio_atual.posicao_2, sorteio_atual.posicao_3,
                sorteio_atual.posicao_4, sorteio_atual.posicao_5, sorteio_atual.posicao_6,
                sorteio_atual.posicao_7
            ])

            numeros_anterior = set([
                sorteio_anterior.posicao_1, sorteio_anterior.posicao_2, sorteio_anterior.posicao_3,
                sorteio_anterior.posicao_4, sorteio_anterior.posicao_5, sorteio_anterior.posicao_6,
                sorteio_anterior.posicao_7
            ])

            repeticoes = numeros_atual & numeros_anterior
            qtd_repeticoes = len(repeticoes)
            contador_repeticoes[qtd_repeticoes] += 1

            if qtd_repeticoes > 0:
                detalhes.append({
                    'concurso_anterior': sorteio_anterior.concurso,
                    'concurso_atual': sorteio_atual.concurso,
                    'quantidade': qtd_repeticoes,
                    'dezenas': sorted(list(repeticoes)),
                    'intervalo': sorteio_atual.concurso - sorteio_anterior.concurso
                })

        total = len(sorteios) - 1
        estatisticas = {}
        for qtd, freq in sorted(contador_repeticoes.items()):
            estatisticas[qtd] = {
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2)
            }

        return {
            'total_comparacoes': total,
            'estatisticas': estatisticas,
            'detalhes': sorted(detalhes, key=lambda x: x['quantidade'], reverse=True)[:20],
            'mais_comum': max(contador_repeticoes.items(), key=lambda x: x[1])[0] if contador_repeticoes else 0
        }

    @staticmethod
    def gerar_matriz_comparacao_dezenas(sorteios):
        """Gera matriz de comparação de dezenas entre todos os jogos premiados"""
        if not sorteios:
            return []

        matriz = []

        # Pegar apenas os últimos 20 jogos para não sobrecarregar
        ultimos_jogos = sorteios[-20:] if len(sorteios) > 20 else sorteios

        for sorteio in ultimos_jogos:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]

            # Criar linha da matriz (1-31)
            linha = []
            for dezena in range(1, 32):
                linha.append(1 if dezena in numeros else 0)

            matriz.append({
                'concurso': sorteio.concurso,
                'linha': linha,
                'numeros': sorted(numeros)
            })

        return matriz

    @staticmethod
    def analisar_numeros_altos():
        """
        Analisa sorteios cujo MENOR número (quando ordenado) é >= 10
        Retorna lista completa de sorteios e estatísticas sobre eles
        """
        # Buscar TODOS os sorteios e filtrar em Python onde o MENOR número >= 10
        todos_sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        # Filtrar sorteios onde o MENOR número (ordenado) >= 10
        sorteios_numeros_altos = []
        for sorteio in todos_sorteios:
            numeros = [
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ]
            # Se o MENOR número for >= 10, incluir
            if min(numeros) >= 10:
                sorteios_numeros_altos.append(sorteio)

        if not sorteios_numeros_altos:
            return {
                'erro': 'Nenhum sorteio com primeiro número >= 10 encontrado',
                'total_sorteios_filtrados': 0,
                'lista_sorteios': []
            }

        total_geral = Sorteio.query.count()
        total_filtrados = len(sorteios_numeros_altos)

        # Gerar lista completa de sorteios para tabela
        lista_sorteios = []
        total_premios = 0
        total_acumulados = 0
        contador_meses = Counter()
        contador_pares_impares = Counter()
        soma_total_geral = 0
        primeira_data = None
        ultima_data = None

        for sorteio in sorteios_numeros_altos:
            numeros = sorted([
                sorteio.posicao_1, sorteio.posicao_2, sorteio.posicao_3,
                sorteio.posicao_4, sorteio.posicao_5, sorteio.posicao_6,
                sorteio.posicao_7
            ])

            # Calcular pares e ímpares
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 7 - pares
            padrao_pi = f"{pares}P/{impares}I"

            # Soma
            soma = sum(numeros)
            soma_total_geral += soma

            # Verificar se teve prêmio
            premiou = sorteio.ganhadores_7_acertos > 0
            if premiou:
                total_premios += 1

            # Verificar se acumulou
            if sorteio.acumulado or sorteio.ganhadores_7_acertos == 0:
                total_acumulados += 1

            # Contadores para estatísticas
            contador_meses[sorteio.mes_sorte] += 1
            contador_pares_impares[padrao_pi] += 1

            # Datas
            if sorteio.data_sorteio:
                if primeira_data is None or sorteio.data_sorteio < primeira_data:
                    primeira_data = sorteio.data_sorteio
                if ultima_data is None or sorteio.data_sorteio > ultima_data:
                    ultima_data = sorteio.data_sorteio

            lista_sorteios.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '-',
                'numeros': numeros,
                'mes_sorte': sorteio.mes_sorte,
                'mes_nome': AnaliseFrequenciaPremiosService.obter_nome_mes(sorteio.mes_sorte),
                'premiou': premiou,
                'ganhadores': sorteio.ganhadores_7_acertos if premiou else 0,
                'valor_premio': sorteio.valor_premio_7_acertos if premiou else 0,
                'pares': pares,
                'impares': impares,
                'padrao_pi': padrao_pi,
                'soma': soma,
                'acumulado': sorteio.acumulado or sorteio.ganhadores_7_acertos == 0
            })

        # Calcular estatísticas
        percentual_filtrados = round((total_filtrados / total_geral) * 100, 2) if total_geral > 0 else 0
        percentual_premios = round((total_premios / total_filtrados) * 100, 2) if total_filtrados > 0 else 0
        media_soma = round(soma_total_geral / total_filtrados, 2) if total_filtrados > 0 else 0

        # Top 3 meses
        top_meses = [
            {
                'mes': mes,
                'mes_nome': AnaliseFrequenciaPremiosService.obter_nome_mes(mes),
                'frequencia': freq,
                'percentual': round((freq / total_filtrados) * 100, 2)
            }
            for mes, freq in contador_meses.most_common(3)
        ]

        # Top 3 padrões pares/ímpares
        top_padroes_pi = [
            {
                'padrao': padrao,
                'frequencia': freq,
                'percentual': round((freq / total_filtrados) * 100, 2)
            }
            for padrao, freq in contador_pares_impares.most_common(3)
        ]

        return {
            'total_sorteios_geral': total_geral,
            'total_sorteios_filtrados': total_filtrados,
            'percentual_filtrados': percentual_filtrados,
            'criterio': 'Menor número (ordenado) >= 10',

            # Lista completa de sorteios
            'lista_sorteios': lista_sorteios,

            # Estatísticas gerais
            'total_premios_7_acertos': total_premios,
            'percentual_premios': percentual_premios,
            'total_acumulados': total_acumulados,
            'percentual_acumulados': round((total_acumulados / total_filtrados) * 100, 2) if total_filtrados > 0 else 0,

            # Período
            'primeira_data': primeira_data.strftime('%d/%m/%Y') if primeira_data else '-',
            'ultima_data': ultima_data.strftime('%d/%m/%Y') if ultima_data else '-',

            # Médias
            'media_soma': media_soma,

            # Top 3
            'top_3_meses': top_meses,
            'top_3_padroes_pi': top_padroes_pi
        }

    def obter_nome_mes(numero):
        """Retorna nome do mês"""
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
