from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseQuadrantesService:
    """
    Serviço para análise de quadrantes do Dia de Sorte
    Baseado na disposição REAL do volante com layout 10 colunas x 4 linhas:

    Linha 1: 01 02 03 04 05 06 07 08 09 10
    Linha 2: 11 12 13 14 15 16 17 18 19 20
    Linha 3: 21 22 23 24 25 26 27 28 29 30
    Linha 4: 31

    Quadrantes (2 linhas x 5 colunas cada):
    Q1: 01-05, 11-15 | Q2: 06-10, 16-20
    Q3: 21-25        | Q4: 26-30
    Q5: 31 (sozinho)
    """

    # Mapeamento dos QUADRANTES baseado no layout REAL do volante (10 colunas)
    # Layout visual:
    # [  Q1 (01-05)  |  Q2 (06-10)  ]  <- Linha 1
    # [  Q1 (11-15)  |  Q2 (16-20)  ]  <- Linha 2
    # [  Q3 (21-25)  |  Q4 (26-30)  ]  <- Linha 3
    # [       Q5 (31)               ]  <- Linha 4
    QUADRANTES = {
        1: [1, 2, 3, 4, 5, 11, 12, 13, 14, 15],      # Superior Esquerdo (L1+L2, C1-5)
        2: [6, 7, 8, 9, 10, 16, 17, 18, 19, 20],     # Superior Direito (L1+L2, C6-10)
        3: [21, 22, 23, 24, 25],                      # Inferior Esquerdo (L3, C1-5)
        4: [26, 27, 28, 29, 30],                      # Inferior Direito (L3, C6-10)
        5: [31]                                        # Linha 4 (isolado)
    }

    # Linhas horizontais do volante (layout 10 colunas)
    LINHAS = {
        'Linha 1': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'Linha 2': [11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
        'Linha 3': [21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
        'Linha 4': [31]
    }

    # Colunas verticais (10 colunas)
    COLUNAS = {
        'Coluna 1': [1, 11, 21, 31],
        'Coluna 2': [2, 12, 22],
        'Coluna 3': [3, 13, 23],
        'Coluna 4': [4, 14, 24],
        'Coluna 5': [5, 15, 25],
        'Coluna 6': [6, 16, 26],
        'Coluna 7': [7, 17, 27],
        'Coluna 8': [8, 18, 28],
        'Coluna 9': [9, 19, 29],
        'Coluna 10': [10, 20, 30]
    }

    # Regiões do volante
    REGIOES = {
        'Início (1-10)': list(range(1, 11)),
        'Meio (11-20)': list(range(11, 21)),
        'Fim (21-31)': list(range(21, 32))
    }

    # Mapeamento de números para linha
    NUMERO_PARA_LINHA = {}
    for linha_nome, nums in LINHAS.items():
        for n in nums:
            NUMERO_PARA_LINHA[n] = linha_nome

    # Mapeamento de números para quadrante
    NUMERO_PARA_QUADRANTE = {}
    for q, nums in QUADRANTES.items():
        for n in nums:
            NUMERO_PARA_QUADRANTE[n] = q

    @staticmethod
    def definir_quadrante(numero):
        """Define qual quadrante (1-5) um número pertence"""
        return AnaliseQuadrantesService.NUMERO_PARA_QUADRANTE.get(numero, None)

    @staticmethod
    def definir_linha(numero):
        """Define qual linha (1-4) um número pertence"""
        return AnaliseQuadrantesService.NUMERO_PARA_LINHA.get(numero, None)

    @staticmethod
    def obter_vizinhos(numero):
        """Retorna os números vizinhos no volante (adjacentes horizontal/vertical)"""
        vizinhos_map = {
            # Linha 1
            1: [2, 11], 2: [1, 3, 12], 3: [2, 4, 13], 4: [3, 5, 14], 5: [4, 6, 15],
            6: [5, 7, 16], 7: [6, 8, 17], 8: [7, 9, 18], 9: [8, 10, 19], 10: [9, 20],
            # Linha 2
            11: [1, 12, 21], 12: [2, 11, 13, 22], 13: [3, 12, 14, 23], 14: [4, 13, 15, 24], 15: [5, 14, 16, 25],
            16: [6, 15, 17, 26], 17: [7, 16, 18, 27], 18: [8, 17, 19, 28], 19: [9, 18, 20, 29], 20: [10, 19, 30],
            # Linha 3
            21: [11, 22, 31], 22: [12, 21, 23], 23: [13, 22, 24], 24: [14, 23, 25], 25: [15, 24, 26],
            26: [16, 25, 27], 27: [17, 26, 28], 28: [18, 27, 29], 29: [19, 28, 30], 30: [20, 29],
            # Linha 4
            31: [21]
        }
        return vizinhos_map.get(numero, [])

    @staticmethod
    def analisar_quadrantes():
        """Análise completa dos quadrantes"""
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        # Contadores de frequência (agora 5 quadrantes)
        frequencia_por_quadrante = {i: 0 for i in range(1, 6)}
        frequencia_padroes = defaultdict(lambda: {
            'frequencia': 0,
            'ultimo_concurso': 0,
            'concursos': []
        })

        soma_quadrantes = {i: 0 for i in range(1, 6)}

        # Análise de vizinhos
        numeros_com_vizinhos = 0
        total_numeros_sorteados = 0

        # Frequência individual de cada número (1-31)
        frequencia_numeros = {i: 0 for i in range(1, 32)}

        # Análise de linhas e colunas
        freq_linhas = defaultdict(int)
        freq_colunas = defaultdict(int)
        freq_regioes = defaultdict(int)

        # Análise de cruzamento Quadrante x Linha
        cruzamento_quadrante_linha = defaultdict(int)

        for sorteio in sorteios:
            numeros = []
            distribuicao_quadrantes = {i: [] for i in range(1, 6)}
            distribuicao_linhas = {linha: [] for linha in AnaliseQuadrantesService.LINHAS.keys()}

            # Coletar números do sorteio
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
                    total_numeros_sorteados += 1

                    # Contar frequência individual
                    frequencia_numeros[numero] += 1

                    # Quadrante
                    quadrante = AnaliseQuadrantesService.definir_quadrante(numero)
                    if quadrante:
                        distribuicao_quadrantes[quadrante].append(numero)
                        frequencia_por_quadrante[quadrante] += 1

                    # Linha
                    linha = AnaliseQuadrantesService.definir_linha(numero)
                    if linha:
                        distribuicao_linhas[linha].append(numero)

                    # Cruzamento Quadrante x Linha
                    if quadrante and linha:
                        chave_cruzamento = f"Q{quadrante} x {linha}"
                        cruzamento_quadrante_linha[chave_cruzamento] += 1

                    # Analisar vizinhos
                    vizinhos = AnaliseQuadrantesService.obter_vizinhos(numero)
                    if any(v in numeros for v in vizinhos):
                        numeros_com_vizinhos += 1

            # Contar por quadrante
            qtd_por_quadrante = {i: len(distribuicao_quadrantes[i]) for i in range(1, 6)}

            for q in range(1, 6):
                soma_quadrantes[q] += qtd_por_quadrante[q]

            # Criar padrão (agora 5 quadrantes)
            padrao_parts = [f"Q{i}:{qtd_por_quadrante[i]}" for i in range(1, 6)]
            padrao = " ".join(padrao_parts)

            frequencia_padroes[padrao]['frequencia'] += 1
            frequencia_padroes[padrao]['concursos'].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                **{f'q{i}': sorted(distribuicao_quadrantes[i]) for i in range(1, 6)}
            })

            if sorteio.concurso > frequencia_padroes[padrao]['ultimo_concurso']:
                frequencia_padroes[padrao]['ultimo_concurso'] = sorteio.concurso

            # Análise de linhas - contar quantos números em cada linha
            for linha_nome, linha_nums in AnaliseQuadrantesService.LINHAS.items():
                qtd = sum(1 for n in numeros if n in linha_nums)
                freq_linhas[f"{linha_nome} ({qtd})"] += 1

            # Análise de colunas
            for col_nome, col_nums in AnaliseQuadrantesService.COLUNAS.items():
                qtd = sum(1 for n in numeros if n in col_nums)
                if qtd > 0:
                    freq_colunas[f"{col_nome} ({qtd})"] += 1

            # Análise de regiões
            for regiao_nome, regiao_nums in AnaliseQuadrantesService.REGIOES.items():
                qtd = sum(1 for n in numeros if n in regiao_nums)
                freq_regioes[f"{regiao_nome} ({qtd})"] += 1

        # Calcular médias (agora 5 quadrantes)
        media_quadrantes = {i: round(soma_quadrantes[i] / total_concursos, 2) for i in range(1, 6)}

        # Processar padrões
        padroes_lista = []
        for padrao, dados in frequencia_padroes.items():
            percentual = round((dados['frequencia'] / total_concursos * 100), 2)
            atraso = ultimo_concurso - dados['ultimo_concurso']

            # Parse padrão (agora 5 quadrantes)
            partes = padrao.split()
            qtd_quadrantes = {i: int(partes[i-1].split(':')[1]) for i in range(1, 6)}

            equilibrio = max(qtd_quadrantes.values()) - min(qtd_quadrantes.values())

            padroes_lista.append({
                'padrao': padrao,
                **{f'q{i}': qtd_quadrantes[i] for i in range(1, 6)},
                'frequencia': dados['frequencia'],
                'percentual': percentual,
                'ultimo_concurso': dados['ultimo_concurso'],
                'atraso': atraso,
                'equilibrio': equilibrio,
                'concursos': dados['concursos']
            })

        padroes_lista.sort(key=lambda x: x['frequencia'], reverse=True)

        # Percentual de números com vizinhos
        perc_vizinhos = round((numeros_com_vizinhos / total_numeros_sorteados * 100), 2) if total_numeros_sorteados > 0 else 0

        # Encontrar max e min frequência
        freq_valores = [f for f in frequencia_numeros.values() if f > 0]
        max_freq = max(freq_valores) if freq_valores else 0
        min_freq = min(freq_valores) if freq_valores else 0

        # Ordenar cruzamento Quadrante x Linha
        cruzamento_ordenado = dict(sorted(cruzamento_quadrante_linha.items(),
                                          key=lambda x: x[1], reverse=True))

        # Top 3 Linhas (frequência total de números por linha)
        freq_total_linhas = {}
        for linha_nome, linha_nums in AnaliseQuadrantesService.LINHAS.items():
            freq_total_linhas[linha_nome] = sum(frequencia_numeros.get(n, 0) for n in linha_nums)

        top3_linhas = sorted(freq_total_linhas.items(), key=lambda x: x[1], reverse=True)[:3]

        return {
            'total_concursos': total_concursos,
            'frequencia_por_quadrante': frequencia_por_quadrante,
            'media_quadrantes': media_quadrantes,
            'frequencia_numeros': frequencia_numeros,
            'max_freq': max_freq,
            'min_freq': min_freq,
            'padroes': padroes_lista,
            'analise_vizinhos': {
                'total_com_vizinhos': numeros_com_vizinhos,
                'total_numeros': total_numeros_sorteados,
                'percentual': perc_vizinhos
            },
            'analise_linhas': dict(freq_linhas),
            'analise_colunas': dict(freq_colunas),
            'analise_regioes': dict(freq_regioes),
            'cruzamento_quadrante_linha': cruzamento_ordenado,
            'top3_linhas': [{'linha': l[0], 'frequencia': l[1]} for l in top3_linhas],
            'quadrantes_config': AnaliseQuadrantesService.QUADRANTES,
            'linhas_config': AnaliseQuadrantesService.LINHAS
        }
