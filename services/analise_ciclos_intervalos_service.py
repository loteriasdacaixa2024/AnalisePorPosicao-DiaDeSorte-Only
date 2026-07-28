from collections import defaultdict
from models import Sorteio


class AnaliseCiclosIntervalosService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'ciclos_dezenas': AnaliseCiclosIntervalosService.calcular_ciclos_dezenas(sorteios),
            'ciclos_meses': AnaliseCiclosIntervalosService.calcular_ciclos_meses(sorteios),
            'intervalos_medios_dezenas': AnaliseCiclosIntervalosService.calcular_intervalos_medios_dezenas(sorteios),
            'intervalos_medios_meses': AnaliseCiclosIntervalosService.calcular_intervalos_medios_meses(sorteios),
            'previsao_proxima_aparicao': AnaliseCiclosIntervalosService.prever_proximas_aparicoes(sorteios)
        }

    @staticmethod
    def calcular_ciclos_dezenas(sorteios):
        ultimas_aparicoes = {}
        intervalos = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                if numero in ultimas_aparicoes:
                    intervalo = idx - ultimas_aparicoes[numero]
                    intervalos[numero].append(intervalo)

                ultimas_aparicoes[numero] = idx

        resultado = []
        for dezena in range(1, 32):
            if dezena in intervalos and intervalos[dezena]:
                resultado.append({
                    'dezena': dezena,
                    'total_aparicoes': len(intervalos[dezena]) + 1,
                    'intervalo_minimo': min(intervalos[dezena]),
                    'intervalo_maximo': max(intervalos[dezena]),
                    'intervalo_medio': round(sum(intervalos[dezena]) / len(intervalos[dezena]), 2),
                    'ultimo_sorteio': ultimas_aparicoes.get(dezena, 0),
                    'atraso_atual': len(sorteios) - 1 - ultimas_aparicoes.get(dezena, 0)
                })

        return sorted(resultado, key=lambda x: x['intervalo_medio'])

    @staticmethod
    def calcular_ciclos_meses(sorteios):
        ultimas_aparicoes = {}
        intervalos = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            mes = sorteio.mes_sorte

            if mes in ultimas_aparicoes:
                intervalo = idx - ultimas_aparicoes[mes]
                intervalos[mes].append(intervalo)

            ultimas_aparicoes[mes] = idx

        resultado = []
        for mes in range(1, 13):
            if mes in intervalos and intervalos[mes]:
                resultado.append({
                    'mes': mes,
                    'mes_nome': AnaliseCiclosIntervalosService.obter_nome_mes(mes),
                    'total_aparicoes': len(intervalos[mes]) + 1,
                    'intervalo_minimo': min(intervalos[mes]),
                    'intervalo_maximo': max(intervalos[mes]),
                    'intervalo_medio': round(sum(intervalos[mes]) / len(intervalos[mes]), 2),
                    'ultimo_sorteio': ultimas_aparicoes.get(mes, 0),
                    'atraso_atual': len(sorteios) - 1 - ultimas_aparicoes.get(mes, 0)
                })

        return sorted(resultado, key=lambda x: x['atraso_atual'], reverse=True)

    @staticmethod
    def calcular_intervalos_medios_dezenas(sorteios):
        ultimas_aparicoes = {}
        intervalos = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                if numero in ultimas_aparicoes:
                    intervalos[numero].append(idx - ultimas_aparicoes[numero])
                ultimas_aparicoes[numero] = idx

        resultado = []
        for dezena in range(1, 32):
            if intervalos[dezena]:
                media = sum(intervalos[dezena]) / len(intervalos[dezena])
                resultado.append({
                    'dezena': dezena,
                    'intervalo_medio': round(media, 2),
                    'desvio_padrao': round(AnaliseCiclosIntervalosService.calcular_desvio_padrao(intervalos[dezena]), 2),
                    'regularidade': 'Alta' if AnaliseCiclosIntervalosService.calcular_desvio_padrao(intervalos[dezena]) < 5 else 'Média' if AnaliseCiclosIntervalosService.calcular_desvio_padrao(intervalos[dezena]) < 10 else 'Baixa'
                })

        return sorted(resultado, key=lambda x: x['intervalo_medio'])

    @staticmethod
    def calcular_intervalos_medios_meses(sorteios):
        ultimas_aparicoes = {}
        intervalos = defaultdict(list)

        for idx, sorteio in enumerate(sorteios):
            mes = sorteio.mes_sorte

            if mes in ultimas_aparicoes:
                intervalos[mes].append(idx - ultimas_aparicoes[mes])
            ultimas_aparicoes[mes] = idx

        resultado = []
        for mes in range(1, 13):
            if intervalos[mes]:
                media = sum(intervalos[mes]) / len(intervalos[mes])
                resultado.append({
                    'mes': mes,
                    'mes_nome': AnaliseCiclosIntervalosService.obter_nome_mes(mes),
                    'intervalo_medio': round(media, 2),
                    'desvio_padrao': round(AnaliseCiclosIntervalosService.calcular_desvio_padrao(intervalos[mes]), 2)
                })

        return sorted(resultado, key=lambda x: x['intervalo_medio'])

    @staticmethod
    def prever_proximas_aparicoes(sorteios):
        ciclos_dezenas = AnaliseCiclosIntervalosService.calcular_ciclos_dezenas(sorteios)
        ciclos_meses = AnaliseCiclosIntervalosService.calcular_ciclos_meses(sorteios)

        dezenas_previstas = sorted([
            {
                'dezena': c['dezena'],
                'previsao': c['atraso_atual'] >= c['intervalo_medio'],
                'score': round((c['atraso_atual'] / c['intervalo_medio']) * 100, 2) if c['intervalo_medio'] > 0 else 0
            }
            for c in ciclos_dezenas
        ], key=lambda x: x['score'], reverse=True)[:15]

        meses_previstos = sorted([
            {
                'mes': c['mes'],
                'mes_nome': c['mes_nome'],
                'previsao': c['atraso_atual'] >= c['intervalo_medio'],
                'score': round((c['atraso_atual'] / c['intervalo_medio']) * 100, 2) if c['intervalo_medio'] > 0 else 0
            }
            for c in ciclos_meses
        ], key=lambda x: x['score'], reverse=True)[:3]

        return {
            'dezenas_com_maior_probabilidade': dezenas_previstas,
            'meses_com_maior_probabilidade': meses_previstos
        }

    @staticmethod
    def calcular_desvio_padrao(valores):
        if not valores:
            return 0
        media = sum(valores) / len(valores)
        variancia = sum((x - media) ** 2 for x in valores) / len(valores)
        return variancia ** 0.5

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
