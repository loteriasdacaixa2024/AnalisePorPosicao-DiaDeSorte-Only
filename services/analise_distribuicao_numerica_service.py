from collections import defaultdict, Counter
from models import Sorteio


class AnaliseDistribuicaoNumericaService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'distribuicao_pares_impares': AnaliseDistribuicaoNumericaService.analisar_pares_impares(sorteios),
            'distribuicao_por_faixas': AnaliseDistribuicaoNumericaService.analisar_faixas_numericas(sorteios),
            'distribuicao_soma_dezenas': AnaliseDistribuicaoNumericaService.analisar_somas(sorteios),
            'dezenas_extremas': AnaliseDistribuicaoNumericaService.analisar_extremos(sorteios),
            'padroes_distribuicao': AnaliseDistribuicaoNumericaService.identificar_padroes_distribuicao(sorteios)
        }

    @staticmethod
    def analisar_pares_impares(sorteios):
        distribuicao = Counter()

        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = len(numeros) - pares

            distribuicao[f"{pares}P-{impares}I"] += 1

        total = len(sorteios)
        resultado = []

        for padrao, freq in distribuicao.most_common():
            resultado.append({
                'padrao': padrao,
                'frequencia': freq,
                'percentual': round((freq / total * 100), 2)
            })

        return {
            'distribuicao_completa': resultado,
            'padrao_mais_comum': resultado[0] if resultado else None
        }

    @staticmethod
    def analisar_faixas_numericas(sorteios):
        # Divide em 4 faixas: 1-8, 9-15, 16-23, 24-31
        faixas_config = {
            'Faixa 1 (1-8)': (1, 8),
            'Faixa 2 (9-15)': (9, 15),
            'Faixa 3 (16-23)': (16, 23),
            'Faixa 4 (24-31)': (24, 31)
        }

        distribuicao_por_sorteio = []
        contadores_faixas = {faixa: 0 for faixa in faixas_config.keys()}

        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            contagem_faixas = {faixa: 0 for faixa in faixas_config.keys()}

            for numero in numeros:
                for faixa, (inicio, fim) in faixas_config.items():
                    if inicio <= numero <= fim:
                        contagem_faixas[faixa] += 1
                        contadores_faixas[faixa] += 1
                        break

            distribuicao_por_sorteio.append(contagem_faixas)

        # Padrões mais comuns
        padroes = Counter()
        for dist in distribuicao_por_sorteio:
            padrao = '-'.join([str(dist[f]) for f in sorted(faixas_config.keys())])
            padroes[padrao] += 1

        resultado_padroes = []
        total = len(sorteios)

        for padrao, freq in padroes.most_common(10):
            resultado_padroes.append({
                'padrao': padrao,
                'frequencia': freq,
                'percentual': round((freq / total * 100), 2)
            })

        resultado_faixas = []
        for faixa in sorted(faixas_config.keys()):
            resultado_faixas.append({
                'faixa': faixa,
                'total_aparicoes': contadores_faixas[faixa],
                'media_por_sorteio': round(contadores_faixas[faixa] / total, 2)
            })

        return {
            'distribuicao_por_faixa': resultado_faixas,
            'padroes_mais_comuns': resultado_padroes
        }

    @staticmethod
    def analisar_somas(sorteios):
        somas = []

        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            soma = sum(numeros)
            somas.append({
                'concurso': sorteio.concurso,
                'soma': soma
            })

        total_somas = [s['soma'] for s in somas]

        return {
            'soma_minima': min(total_somas),
            'soma_maxima': max(total_somas),
            'soma_media': round(sum(total_somas) / len(total_somas), 2),
            'distribuicao_por_faixas': AnaliseDistribuicaoNumericaService.distribuir_somas_por_faixas(total_somas),
            'ultimas_somas': somas[-20:]
        }

    @staticmethod
    def distribuir_somas_por_faixas(somas):
        # Faixas de soma: Muito Baixa, Baixa, Média, Alta, Muito Alta
        minima = min(somas)
        maxima = max(somas)
        range_total = maxima - minima
        tamanho_faixa = range_total / 5

        faixas = {
            'Muito Baixa': (minima, minima + tamanho_faixa),
            'Baixa': (minima + tamanho_faixa, minima + 2 * tamanho_faixa),
            'Média': (minima + 2 * tamanho_faixa, minima + 3 * tamanho_faixa),
            'Alta': (minima + 3 * tamanho_faixa, minima + 4 * tamanho_faixa),
            'Muito Alta': (minima + 4 * tamanho_faixa, maxima + 1)
        }

        contador_faixas = Counter()
        for soma in somas:
            for nome_faixa, (inicio, fim) in faixas.items():
                if inicio <= soma < fim:
                    contador_faixas[nome_faixa] += 1
                    break

        resultado = []
        total = len(somas)

        for faixa in ['Muito Baixa', 'Baixa', 'Média', 'Alta', 'Muito Alta']:
            freq = contador_faixas[faixa]
            resultado.append({
                'faixa': faixa,
                'range': f"{int(faixas[faixa][0])}-{int(faixas[faixa][1]-1)}",
                'frequencia': freq,
                'percentual': round((freq / total * 100), 2)
            })

        return resultado

    @staticmethod
    def analisar_extremos(sorteios):
        menores = []
        maiores = []

        for sorteio in sorteios:
            numeros = sorteio.get_posicoes_lista()
            menores.append(min(numeros))
            maiores.append(max(numeros))

        contador_menores = Counter(menores)
        contador_maiores = Counter(maiores)

        return {
            'menor_numero_mais_frequente': [
                {
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios) * 100), 2)
                }
                for num, freq in contador_menores.most_common(10)
            ],
            'maior_numero_mais_frequente': [
                {
                    'numero': num,
                    'frequencia': freq,
                    'percentual': round((freq / len(sorteios) * 100), 2)
                }
                for num, freq in contador_maiores.most_common(10)
            ],
            'amplitude_media': round(sum(maiores) / len(maiores) - sum(menores) / len(menores), 2)
        }

    @staticmethod
    def identificar_padroes_distribuicao(sorteios):
        # Analisa sequências e saltos
        padroes = {
            'com_sequencia': 0,
            'sem_sequencia': 0,
            'alta_dispersao': 0,
            'baixa_dispersao': 0
        }

        for sorteio in sorteios:
            numeros = sorted(sorteio.get_posicoes_lista())

            # Verifica sequências
            tem_sequencia = False
            for i in range(len(numeros) - 1):
                if numeros[i+1] - numeros[i] == 1:
                    tem_sequencia = True
                    break

            if tem_sequencia:
                padroes['com_sequencia'] += 1
            else:
                padroes['sem_sequencia'] += 1

            # Verifica dispersão (média dos intervalos)
            intervalos = [numeros[i+1] - numeros[i] for i in range(len(numeros) - 1)]
            media_intervalo = sum(intervalos) / len(intervalos)

            if media_intervalo > 4:
                padroes['alta_dispersao'] += 1
            else:
                padroes['baixa_dispersao'] += 1

        total = len(sorteios)
        return {
            'com_sequencia': {
                'quantidade': padroes['com_sequencia'],
                'percentual': round((padroes['com_sequencia'] / total * 100), 2)
            },
            'sem_sequencia': {
                'quantidade': padroes['sem_sequencia'],
                'percentual': round((padroes['sem_sequencia'] / total * 100), 2)
            },
            'alta_dispersao': {
                'quantidade': padroes['alta_dispersao'],
                'percentual': round((padroes['alta_dispersao'] / total * 100), 2)
            },
            'baixa_dispersao': {
                'quantidade': padroes['baixa_dispersao'],
                'percentual': round((padroes['baixa_dispersao'] / total * 100), 2)
            }
        }
