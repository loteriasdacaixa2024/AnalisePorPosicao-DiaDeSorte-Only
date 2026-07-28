from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseRaizDigitalService:

    @staticmethod
    def calcular_raiz_digital(numero):
        while numero >= 10:
            soma = 0
            while numero > 0:
                soma += numero % 10
                numero //= 10
            numero = soma
        return numero

    @staticmethod
    def analisar_raiz_digital():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        frequencia_raizes = defaultdict(int)
        frequencia_padroes = defaultdict(lambda: {
            'frequencia': 0,
            'ultimo_concurso': 0,
            'concursos': []
        })

        soma_raizes = defaultdict(int)

        for sorteio in sorteios:
            numeros = []
            raizes = []
            distribuicao_raizes = defaultdict(int)

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
                    raiz = AnaliseRaizDigitalService.calcular_raiz_digital(numero)
                    raizes.append(raiz)
                    frequencia_raizes[raiz] += 1
                    distribuicao_raizes[raiz] += 1

            for raiz in range(1, 10):
                soma_raizes[raiz] += distribuicao_raizes.get(raiz, 0)

            raizes_ordenadas = sorted(raizes)
            padrao = '-'.join(map(str, raizes_ordenadas))

            frequencia_padroes[padrao]['frequencia'] += 1
            frequencia_padroes[padrao]['concursos'].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                'raizes': raizes_ordenadas
            })

            if sorteio.concurso > frequencia_padroes[padrao]['ultimo_concurso']:
                frequencia_padroes[padrao]['ultimo_concurso'] = sorteio.concurso

        distribuicao_raizes = []
        for raiz in range(1, 10):
            freq = frequencia_raizes[raiz]
            percentual = round((freq / sum(frequencia_raizes.values()) * 100), 2)
            media_por_sorteio = round(soma_raizes[raiz] / total_concursos, 2)

            distribuicao_raizes.append({
                'raiz': raiz,
                'frequencia': freq,
                'porcentagem': percentual,
                'media_por_sorteio': media_por_sorteio
            })

        distribuicao_raizes.sort(key=lambda x: x['frequencia'], reverse=True)

        padroes_lista = []
        for padrao, dados in frequencia_padroes.items():
            percentual = round((dados['frequencia'] / total_concursos * 100), 2)
            atraso = ultimo_concurso - dados['ultimo_concurso']

            padroes_lista.append({
                'padrao': padrao,
                'frequencia': dados['frequencia'],
                'percentual': percentual,
                'ultimo_concurso': dados['ultimo_concurso'],
                'atraso': atraso,
                'concursos': dados['concursos']
            })

        padroes_lista.sort(key=lambda x: x['frequencia'], reverse=True)

        numeros_por_raiz = defaultdict(list)
        for num in range(1, 32):
            raiz = AnaliseRaizDigitalService.calcular_raiz_digital(num)
            numeros_por_raiz[raiz].append(num)

        mapa_raizes = []
        for raiz in range(1, 10):
            mapa_raizes.append({
                'raiz': raiz,
                'numeros': numeros_por_raiz[raiz]
            })

        return {
            'total_concursos': total_concursos,
            'distribuicao_raizes': distribuicao_raizes,
            'padroes': padroes_lista[:20],
            'mapa_raizes': mapa_raizes
        }