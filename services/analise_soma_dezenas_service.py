from models.sorteio import Sorteio, db
from collections import defaultdict
import statistics

class AnaliseSomaDezenasService:

    @staticmethod
    def analisar_somas():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        somas_por_concurso = []
        frequencia_somas = defaultdict(int)
        ultima_aparicao_soma = {}

        for idx, sorteio in enumerate(sorteios):
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            if len(numeros) == 7:
                soma = sum(numeros)
                somas_por_concurso.append({
                    'concurso': sorteio.concurso,
                    'soma': soma,
                    'numeros': sorted(numeros),
                    'par_impar': 'Par' if soma % 2 == 0 else 'Ímpar'
                })
                frequencia_somas[soma] += 1
                ultima_aparicao_soma[soma] = idx

        if not somas_por_concurso:
            return {'error': 'Nenhum sorteio válido encontrado'}

        todas_somas = [s['soma'] for s in somas_por_concurso]

        soma_minima = min(todas_somas)
        soma_maxima = max(todas_somas)
        soma_media = statistics.mean(todas_somas)
        soma_mediana = statistics.median(todas_somas)
        desvio_padrao = statistics.stdev(todas_somas)

        somas_pares = sum(1 for s in somas_por_concurso if s['par_impar'] == 'Par')
        somas_impares = total_concursos - somas_pares

        faixas = {
            '7-70': 0,
            '71-90': 0,
            '91-110': 0,
            '111-130': 0,
            '131-150': 0,
            '151-170': 0,
            '171-217': 0
        }

        for soma in todas_somas:
            if soma <= 70:
                faixas['7-70'] += 1
            elif soma <= 90:
                faixas['71-90'] += 1
            elif soma <= 110:
                faixas['91-110'] += 1
            elif soma <= 130:
                faixas['111-130'] += 1
            elif soma <= 150:
                faixas['131-150'] += 1
            elif soma <= 170:
                faixas['151-170'] += 1
            else:
                faixas['171-217'] += 1

        ranking_somas = []
        for soma, freq in frequencia_somas.items():
            ultima_vez = ultima_aparicao_soma.get(soma, 0)
            atraso = total_concursos - 1 - ultima_vez
            percentual = round((freq / total_concursos * 100), 2)

            ranking_somas.append({
                'soma': soma,
                'frequencia': freq,
                'percentual': percentual,
                'atraso': atraso,
                'ultima_aparicao': ultima_vez,
                'par_impar': 'Par' if soma % 2 == 0 else 'Ímpar'
            })

        ranking_somas.sort(key=lambda x: x['frequencia'], reverse=True)

        top_10_frequentes = ranking_somas[:10]
        top_10_atrasadas = sorted(ranking_somas, key=lambda x: x['atraso'], reverse=True)[:10]

        somas_nunca_saidas = []
        for soma in range(7, 218):
            if soma not in frequencia_somas:
                somas_nunca_saidas.append(soma)

        return {
            'total_concursos': total_concursos,
            'soma_minima': soma_minima,
            'soma_maxima': soma_maxima,
            'soma_media': round(soma_media, 2),
            'soma_mediana': soma_mediana,
            'desvio_padrao': round(desvio_padrao, 2),
            'somas_pares': somas_pares,
            'somas_impares': somas_impares,
            'percentual_pares': round((somas_pares / total_concursos * 100), 2),
            'percentual_impares': round((somas_impares / total_concursos * 100), 2),
            'faixas': faixas,
            'percentual_faixas': {k: round((v / total_concursos * 100), 2) for k, v in faixas.items()},
            'ranking_somas': ranking_somas,
            'top_10_frequentes': top_10_frequentes,
            'top_10_atrasadas': top_10_atrasadas,
            'somas_nunca_saidas': somas_nunca_saidas,
            'total_somas_diferentes': len(frequencia_somas),
            'ultimos_10_sorteios': somas_por_concurso[-10:]
        }
