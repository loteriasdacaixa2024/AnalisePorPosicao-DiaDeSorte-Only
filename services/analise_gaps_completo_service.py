"""
Service para Análise Completa de Gaps e Dígitos Iniciais
Sistema: Dia de Sorte
Desenvolvido para: Márcio Fernando Maia
"""

from models.sorteio import Sorteio
from collections import Counter, defaultdict
from datetime import datetime
import statistics


class AnaliseGapsCompletoService:
    """
    Service para análises avançadas de gaps (distâncias) e dígitos iniciais
    """

    @staticmethod
    def obter_digito_inicial(numero):
        """
        Retorna o dígito inicial de um número (0, 1, 2 ou 3)

        0 → 01-09
        1 → 10-19
        2 → 20-29
        3 → 30-31

        Args:
            numero: Número de 1 a 31

        Returns:
            int: Dígito inicial (0, 1, 2 ou 3)
        """
        if numero <= 9:
            return 0
        elif numero <= 19:
            return 1
        elif numero <= 29:
            return 2
        else:
            return 3

    @staticmethod
    def calcular_gaps(numeros_ordenados):
        """
        Calcula os gaps (distâncias) entre números consecutivos

        Args:
            numeros_ordenados: Lista de números já ordenados

        Returns:
            list: Lista de gaps
        """
        gaps = []
        for i in range(len(numeros_ordenados) - 1):
            gap = numeros_ordenados[i + 1] - numeros_ordenados[i]
            gaps.append(gap)
        return gaps

    @staticmethod
    def analisar_digitos_iniciais():
        """
        ANÁLISE 1 - Dígitos Iniciais

        Analisa os padrões de dígitos iniciais em todos os concursos

        Returns:
            dict com top 3 padrões, frequências e exemplos
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if not sorteios:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum sorteio encontrado no banco de dados'
                }

            # Coletar todos os padrões de dígitos
            padroes_digitos = []
            padroes_detalhados = []

            for sorteio in sorteios:
                # Extrair os 7 números
                numeros = [
                    sorteio.posicao_1,
                    sorteio.posicao_2,
                    sorteio.posicao_3,
                    sorteio.posicao_4,
                    sorteio.posicao_5,
                    sorteio.posicao_6,
                    sorteio.posicao_7
                ]

                # Calcular dígitos iniciais
                digitos = sorted([AnaliseGapsCompletoService.obter_digito_inicial(n) for n in numeros])

                # Padrão como string para contar frequências
                padrao_str = '-'.join(map(str, digitos))
                padroes_digitos.append(padrao_str)

                # Guardar detalhes para exemplos
                padroes_detalhados.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': numeros,
                    'digitos': digitos,
                    'padrao': padrao_str
                })

            # Contar frequências
            contador_padroes = Counter(padroes_digitos)
            top_3_padroes = contador_padroes.most_common(3)

            # Contar frequência de cada dígito individual
            todos_digitos = []
            for padrao in padroes_digitos:
                todos_digitos.extend(padrao.split('-'))

            contador_digitos_individuais = Counter(todos_digitos)

            # Preparar resultado detalhado
            top_3_detalhado = []
            for padrao, frequencia in top_3_padroes:
                # Encontrar exemplos de concursos com esse padrão
                exemplos = [p for p in padroes_detalhados if p['padrao'] == padrao][:5]  # Até 5 exemplos

                # Verificar se aparece recentemente (últimos 10 sorteios)
                ultimos_10 = padroes_digitos[-10:]
                aparece_recente = padrao in ultimos_10

                top_3_detalhado.append({
                    'padrao': padrao,
                    'frequencia': frequencia,
                    'percentual': (frequencia / len(sorteios)) * 100,
                    'aparece_recente': aparece_recente,
                    'exemplos': exemplos
                })

            return {
                'sucesso': True,
                'total_sorteios': len(sorteios),
                'top_3_padroes': top_3_detalhado,
                'digitos_individuais': dict(contador_digitos_individuais.most_common()),
                'mensagem': f'Análise de dígitos iniciais concluída com {len(sorteios)} sorteios'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao analisar dígitos iniciais: {str(e)}'
            }

    @staticmethod
    def analisar_gaps():
        """
        ANÁLISE 2 - Gaps (Distâncias)

        Analisa os gaps entre números consecutivos em todos os concursos

        Returns:
            dict com top 3 gaps, padrões de gaps e exemplos
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if not sorteios:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum sorteio encontrado no banco de dados'
                }

            # Coletar todos os gaps individuais e padrões completos
            todos_gaps = []
            padroes_gaps_completos = []
            padroes_detalhados = []

            for sorteio in sorteios:
                # Extrair e ordenar os 7 números
                numeros = sorted([
                    sorteio.posicao_1,
                    sorteio.posicao_2,
                    sorteio.posicao_3,
                    sorteio.posicao_4,
                    sorteio.posicao_5,
                    sorteio.posicao_6,
                    sorteio.posicao_7
                ])

                # Calcular gaps
                gaps = AnaliseGapsCompletoService.calcular_gaps(numeros)

                # Adicionar gaps individuais
                todos_gaps.extend(gaps)

                # Padrão completo de gaps como string
                padrao_gaps_str = '-'.join(map(str, gaps))
                padroes_gaps_completos.append(padrao_gaps_str)

                # Guardar detalhes
                padroes_detalhados.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': numeros,
                    'gaps': gaps,
                    'padrao_gaps': padrao_gaps_str,
                    'gap_medio': statistics.mean(gaps),
                    'gap_maximo': max(gaps),
                    'gap_minimo': min(gaps)
                })

            # Contar frequências
            contador_gaps_individuais = Counter(todos_gaps)
            contador_padroes_completos = Counter(padroes_gaps_completos)

            top_3_gaps_individuais = contador_gaps_individuais.most_common(3)
            top_3_padroes_completos = contador_padroes_completos.most_common(3)

            # Preparar resultado detalhado - gaps individuais
            top_3_gaps_detalhado = []
            for gap, frequencia in top_3_gaps_individuais:
                top_3_gaps_detalhado.append({
                    'gap': gap,
                    'frequencia': frequencia,
                    'percentual': (frequencia / len(todos_gaps)) * 100
                })

            # Preparar resultado detalhado - padrões completos
            top_3_padroes_detalhado = []
            for padrao, frequencia in top_3_padroes_completos:
                # Encontrar exemplos
                exemplos = [p for p in padroes_detalhados if p['padrao_gaps'] == padrao][:5]

                # Verificar se aparece recentemente
                ultimos_10 = padroes_gaps_completos[-10:]
                aparece_recente = padrao in ultimos_10

                top_3_padroes_detalhado.append({
                    'padrao': padrao,
                    'frequencia': frequencia,
                    'percentual': (frequencia / len(sorteios)) * 100,
                    'aparece_recente': aparece_recente,
                    'exemplos': exemplos
                })

            # Estatísticas gerais
            gap_medio_geral = statistics.mean(todos_gaps)
            gap_mediano = statistics.median(todos_gaps)

            return {
                'sucesso': True,
                'total_sorteios': len(sorteios),
                'total_gaps': len(todos_gaps),
                'gap_medio_geral': gap_medio_geral,
                'gap_mediano': gap_mediano,
                'top_3_gaps_individuais': top_3_gaps_detalhado,
                'top_3_padroes_completos': top_3_padroes_detalhado,
                'mensagem': f'Análise de gaps concluída com {len(sorteios)} sorteios'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao analisar gaps: {str(e)}'
            }

    @staticmethod
    def cruzar_digitos_gaps():
        """
        CRUZAMENTO - Dígitos Iniciais × Gaps

        Analisa a relação entre padrões de dígitos e tamanho dos gaps

        Returns:
            dict com análise cruzada
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if not sorteios:
                return {
                    'sucesso': False,
                    'mensagem': 'Nenhum sorteio encontrado no banco de dados'
                }

            # Estrutura para cruzamento
            cruzamento = defaultdict(lambda: {
                'gaps_curtos': 0,      # gap <= 2
                'gaps_medios': 0,      # 3 <= gap <= 5
                'gaps_longos': 0,      # gap > 5
                'total': 0,
                'gap_medio': [],
                'exemplos': []
            })

            for sorteio in sorteios:
                # Extrair e ordenar os 7 números
                numeros = sorted([
                    sorteio.posicao_1,
                    sorteio.posicao_2,
                    sorteio.posicao_3,
                    sorteio.posicao_4,
                    sorteio.posicao_5,
                    sorteio.posicao_6,
                    sorteio.posicao_7
                ])

                # Calcular dígitos e gaps
                digitos = sorted([AnaliseGapsCompletoService.obter_digito_inicial(n) for n in numeros])
                gaps = AnaliseGapsCompletoService.calcular_gaps(numeros)

                # Padrão de dígitos
                padrao_digitos = '-'.join(map(str, digitos))

                # Classificar gaps
                gap_medio = statistics.mean(gaps)

                cruzamento[padrao_digitos]['total'] += 1
                cruzamento[padrao_digitos]['gap_medio'].append(gap_medio)

                # Contar gaps por tamanho
                for gap in gaps:
                    if gap <= 2:
                        cruzamento[padrao_digitos]['gaps_curtos'] += 1
                    elif gap <= 5:
                        cruzamento[padrao_digitos]['gaps_medios'] += 1
                    else:
                        cruzamento[padrao_digitos]['gaps_longos'] += 1

                # Guardar exemplos (até 3 por padrão)
                if len(cruzamento[padrao_digitos]['exemplos']) < 3:
                    cruzamento[padrao_digitos]['exemplos'].append({
                        'concurso': sorteio.concurso,
                        'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                        'numeros': numeros,
                        'gaps': gaps,
                        'gap_medio': gap_medio
                    })

            # Processar resultados
            resultados = []
            for padrao, dados in cruzamento.items():
                if dados['total'] > 0:
                    # Calcular médias
                    gap_medio_padrao = statistics.mean(dados['gap_medio'])

                    # Percentuais
                    total_gaps = dados['gaps_curtos'] + dados['gaps_medios'] + dados['gaps_longos']

                    perc_curtos = (dados['gaps_curtos'] / total_gaps * 100) if total_gaps > 0 else 0
                    perc_medios = (dados['gaps_medios'] / total_gaps * 100) if total_gaps > 0 else 0
                    perc_longos = (dados['gaps_longos'] / total_gaps * 100) if total_gaps > 0 else 0

                    # Classificação dominante
                    if perc_curtos > perc_medios and perc_curtos > perc_longos:
                        classificacao = 'Gaps Curtos (≤2)'
                    elif perc_longos > perc_medios:
                        classificacao = 'Gaps Longos (>5)'
                    else:
                        classificacao = 'Gaps Médios (3-5)'

                    resultados.append({
                        'padrao_digitos': padrao,
                        'frequencia': dados['total'],
                        'gap_medio': gap_medio_padrao,
                        'gaps_curtos_perc': perc_curtos,
                        'gaps_medios_perc': perc_medios,
                        'gaps_longos_perc': perc_longos,
                        'classificacao_dominante': classificacao,
                        'exemplos': dados['exemplos']
                    })

            # Ordenar por frequência
            resultados.sort(key=lambda x: x['frequencia'], reverse=True)

            # Top 5 padrões mais frequentes
            top_5 = resultados[:5]

            return {
                'sucesso': True,
                'total_padroes': len(resultados),
                'top_5_cruzamentos': top_5,
                'mensagem': 'Cruzamento de dígitos × gaps concluído'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao cruzar análises: {str(e)}'
            }

    @staticmethod
    def sugerir_jogos():
        """
        Sugere jogos baseados nos padrões mais frequentes

        Returns:
            dict com sugestões de jogos
        """
        try:
            # Obter análises
            analise_digitos = AnaliseGapsCompletoService.analisar_digitos_iniciais()
            analise_gaps = AnaliseGapsCompletoService.analisar_gaps()
            cruzamento = AnaliseGapsCompletoService.cruzar_digitos_gaps()

            if not analise_digitos['sucesso'] or not analise_gaps['sucesso']:
                return {
                    'sucesso': False,
                    'mensagem': 'Erro ao gerar sugestões'
                }

            # Pegar padrão de dígitos mais frequente
            padrao_digitos_top = analise_digitos['top_3_padroes'][0]['padrao']
            digitos_top = list(map(int, padrao_digitos_top.split('-')))

            # Pegar padrão de gaps mais frequente
            padrao_gaps_top = analise_gaps['top_3_padroes_completos'][0]['padrao']
            gaps_top = list(map(int, padrao_gaps_top.split('-')))

            # Gerar jogo sugerido baseado nos padrões
            sugestoes = []

            # Sugestão 1: Baseado no padrão de dígitos mais frequente
            jogo_1 = AnaliseGapsCompletoService._gerar_jogo_por_digitos(digitos_top)
            sugestoes.append({
                'tipo': 'Baseado em Dígitos Mais Frequentes',
                'padrao_referencia': padrao_digitos_top,
                'numeros': jogo_1,
                'justificativa': f'Jogo gerado seguindo o padrão de dígitos mais comum: {padrao_digitos_top}'
            })

            # Sugestão 2: Baseado no padrão de gaps mais frequente
            jogo_2 = AnaliseGapsCompletoService._gerar_jogo_por_gaps(gaps_top)
            sugestoes.append({
                'tipo': 'Baseado em Gaps Mais Frequentes',
                'padrao_referencia': padrao_gaps_top,
                'numeros': jogo_2,
                'justificativa': f'Jogo gerado seguindo o padrão de gaps mais comum: {padrao_gaps_top}'
            })

            # Sugestão 3: Cruzamento (dígitos + gaps)
            if cruzamento['sucesso'] and cruzamento['top_5_cruzamentos']:
                cruzamento_top = cruzamento['top_5_cruzamentos'][0]
                exemplo = cruzamento_top['exemplos'][0] if cruzamento_top['exemplos'] else None

                if exemplo:
                    sugestoes.append({
                        'tipo': 'Baseado em Cruzamento (Dígitos × Gaps)',
                        'padrao_referencia': f"{cruzamento_top['padrao_digitos']} | Gaps {cruzamento_top['classificacao_dominante']}",
                        'numeros': exemplo['numeros'],
                        'justificativa': f"Padrão mais frequente com {cruzamento_top['classificacao_dominante']}"
                    })

            return {
                'sucesso': True,
                'sugestoes': sugestoes,
                'mensagem': f'{len(sugestoes)} jogos sugeridos'
            }

        except Exception as e:
            return {
                'sucesso': False,
                'mensagem': f'Erro ao sugerir jogos: {str(e)}'
            }

    @staticmethod
    def _gerar_jogo_por_digitos(digitos):
        """
        Gera um jogo de 7 números baseado em um padrão de dígitos

        Args:
            digitos: Lista de 7 dígitos (ex: [0, 0, 1, 1, 2, 2, 3])

        Returns:
            list: 7 números gerados
        """
        import random

        numeros = []
        for digito in digitos:
            if digito == 0:
                numeros.append(random.randint(1, 9))
            elif digito == 1:
                numeros.append(random.randint(10, 19))
            elif digito == 2:
                numeros.append(random.randint(20, 29))
            else:  # digito == 3
                numeros.append(random.randint(30, 31))

        # Garantir que não há duplicatas
        numeros = list(set(numeros))
        while len(numeros) < 7:
            # Adicionar números aleatórios se necessário
            novo = random.randint(1, 31)
            if novo not in numeros:
                numeros.append(novo)

        return sorted(numeros[:7])

    @staticmethod
    def _gerar_jogo_por_gaps(gaps):
        """
        Gera um jogo de 7 números baseado em um padrão de gaps

        Args:
            gaps: Lista de 6 gaps (ex: [1, 2, 3, 1, 4, 5])

        Returns:
            list: 7 números gerados
        """
        import random

        # Começar com um número inicial aleatório entre 1 e 10
        numero_inicial = random.randint(1, 10)

        numeros = [numero_inicial]

        for gap in gaps:
            proximo = numeros[-1] + gap
            # Garantir que não ultrapassa 31
            if proximo > 31:
                proximo = 31
            numeros.append(proximo)

        # Se algum número passou de 31, ajustar
        if max(numeros) > 31:
            # Recalcular com número inicial menor
            numero_inicial = random.randint(1, 5)
            numeros = [numero_inicial]
            for gap in gaps:
                proximo = numeros[-1] + gap
                if proximo > 31:
                    proximo = 31
                numeros.append(proximo)

        return sorted(list(set(numeros))[:7])

    @staticmethod
    def executar_analise_completa():
        """
        Executa todas as análises de uma vez

        Returns:
            dict com todas as análises
        """
        return {
            'sucesso': True,
            'data_atualizacao': datetime.now().strftime('%d/%m/%Y %H:%M:%S'),
            'digitos': AnaliseGapsCompletoService.analisar_digitos_iniciais(),
            'gaps': AnaliseGapsCompletoService.analisar_gaps(),
            'cruzamento': AnaliseGapsCompletoService.cruzar_digitos_gaps(),
            'sugestoes': AnaliseGapsCompletoService.sugerir_jogos()
        }
