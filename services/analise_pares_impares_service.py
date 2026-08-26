from models.sorteio import Sorteio, db


class AnaliseParesImparesService:
    @staticmethod
    def obter_distribuicao_pares_impares():
        """
        Retorna análise da distribuição de números pares e ímpares nos sorteios.
        Padrões possíveis: 0P+7I, 1P+6I, 2P+5I, 3P+4I, 4P+3I, 5P+2I, 6P+1I, 7P+0I.
        """
        total_concursos = Sorteio.query.count()

        if total_concursos == 0:
            return {
                'padroes': [],
                'total_concursos': 0
            }

        # Dicionário para contar cada padrão (0 a 7 pares)
        contagem_padroes = {i: 0 for i in range(8)}
        ultimos_concursos = {i: None for i in range(8)}

        # Buscar todos os concursos
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        for concurso in concursos:
            # Contar quantos pares existem neste concurso
            qtd_pares = 0

            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)

                if numero and numero % 2 == 0:
                    qtd_pares += 1

            # Incrementar contagem do padrão
            contagem_padroes[qtd_pares] += 1

            # Salvar o último concurso deste padrão
            if ultimos_concursos[qtd_pares] is None:
                ultimos_concursos[qtd_pares] = concurso.concurso

        # Criar lista de padrões
        padroes = []
        for qtd_pares in range(8):
            qtd_impares = 7 - qtd_pares
            freq = contagem_padroes[qtd_pares]
            percentual = round((freq / total_concursos) * 100, 2) if total_concursos > 0 else 0

            ultimo_concurso_geral = Sorteio.query.order_by(Sorteio.concurso.desc()).first()
            atraso = (
                ultimo_concurso_geral.concurso - ultimos_concursos[qtd_pares]
                if ultimos_concursos[qtd_pares]
                else total_concursos
            )

            padroes.append({
                'pares': qtd_pares,
                'impares': qtd_impares,
                'descricao': f'{qtd_pares}P + {qtd_impares}I',
                'frequencia': freq,
                'percentual': f'{percentual:.2f}',
                'ultimo_concurso': ultimos_concursos[qtd_pares] or 0,
                'atraso': atraso
            })

        # Ordenar por frequência (mais comum primeiro)
        padroes.sort(key=lambda x: x['frequencia'], reverse=True)

        # Calcular estatísticas adicionais
        total_pares = sum(p['pares'] * p['frequencia'] for p in padroes)
        media_pares = round(total_pares / total_concursos, 2) if total_concursos > 0 else 0

        return {
            'padroes': padroes,
            'total_concursos': total_concursos,
            'media_pares_por_sorteio': media_pares,
            'media_impares_por_sorteio': round(7 - media_pares, 2)
        }

    @staticmethod
    def obter_historico_recente(limite=50):
        """
        Retorna o histórico dos últimos N concursos com seus padrões.
        """
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).limit(limite).all()

        historico = []
        for concurso in concursos:
            qtd_pares = 0
            numeros_pares = []
            numeros_impares = []

            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)

                if numero:
                    if numero % 2 == 0:
                        qtd_pares += 1
                        numeros_pares.append(numero)
                    else:
                        numeros_impares.append(numero)

            qtd_impares = 7 - qtd_pares

            historico.append({
                'concurso': concurso.concurso,
                'pares': qtd_pares,
                'impares': qtd_impares,
                'descricao': f'{qtd_pares}P + {qtd_impares}I',
                'numeros_pares': sorted(numeros_pares),
                'numeros_impares': sorted(numeros_impares)
            })

        return {
            'historico': historico,
            'total_registros': len(historico)
        }

    @staticmethod
    def obter_padroes_extremos():
        """
        Retorna detalhes dos padrões extremos e quase-extremos:
        - 0P + 7I (todos ímpares)
        - 7P + 0I (todos pares) + ATRASO
        - 1P + 6I (1 par, 6 ímpares)
        - 6P + 1I (6 pares, 1 ímpar)

        Para cada padrão, retorna a lista completa de concursos com os números sorteados.
        """
        # Buscar todos os concursos ordenados por concurso (mais recente primeiro)
        concursos = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not concursos:
            return {
                'padroes_extremos': {},
                'total_concursos': 0
            }

        ultimo_concurso_geral = concursos[0].concurso

        # Estrutura para armazenar os padrões de interesse
        padroes_interesse = {
            '0P_7I': {'pares': 0, 'impares': 7, 'descricao': '0P + 7I', 'concursos': [], 'ultimo': None},
            '7P_0I': {'pares': 7, 'impares': 0, 'descricao': '7P + 0I', 'concursos': [], 'ultimo': None},
            '1P_6I': {'pares': 1, 'impares': 6, 'descricao': '1P + 6I', 'concursos': [], 'ultimo': None},
            '6P_1I': {'pares': 6, 'impares': 1, 'descricao': '6P + 1I', 'concursos': [], 'ultimo': None},
        }

        for concurso in concursos:
            # Coletar números e classificar
            numeros_pares = []
            numeros_impares = []
            todos_numeros = []

            for pos in range(1, 8):
                campo = f'posicao_{pos}'
                numero = getattr(concurso, campo, None)

                if numero:
                    todos_numeros.append(numero)
                    if numero % 2 == 0:
                        numeros_pares.append(numero)
                    else:
                        numeros_impares.append(numero)

            qtd_pares = len(numeros_pares)
            qtd_impares = len(numeros_impares)

            # Verificar se é um padrão de interesse
            chave = f'{qtd_pares}P_{qtd_impares}I'

            if chave in padroes_interesse:
                registro = {
                    'concurso': concurso.concurso,
                    'data': concurso.data_sorteio.strftime('%d/%m/%Y') if concurso.data_sorteio else '',
                    'numeros': sorted(todos_numeros),
                    'numeros_pares': sorted(numeros_pares),
                    'numeros_impares': sorted(numeros_impares)
                }
                padroes_interesse[chave]['concursos'].append(registro)

                # Atualizar último concurso deste padrão
                if padroes_interesse[chave]['ultimo'] is None:
                    padroes_interesse[chave]['ultimo'] = concurso.concurso

        # Calcular frequência e atraso para cada padrão
        resultado = {}
        for chave, dados in padroes_interesse.items():
            frequencia = len(dados['concursos'])
            ultimo = dados['ultimo'] or 0
            atraso = ultimo_concurso_geral - ultimo if ultimo else ultimo_concurso_geral

            resultado[chave] = {
                'descricao': dados['descricao'],
                'pares': dados['pares'],
                'impares': dados['impares'],
                'frequencia': frequencia,
                'ultimo_concurso': ultimo,
                'atraso': atraso,
                'concursos': dados['concursos']  # Lista completa com números
            }

        return {
            'padroes_extremos': resultado,
            'total_concursos': len(concursos),
            'ultimo_concurso_geral': ultimo_concurso_geral
        }
