from collections import defaultdict, Counter
from models import Sorteio
from datetime import datetime


class AnaliseSazonalService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'analise_por_trimestre': AnaliseSazonalService.analisar_trimestres(sorteios),
            'analise_por_semestre': AnaliseSazonalService.analisar_semestres(sorteios),
            'analise_por_estacao': AnaliseSazonalService.analisar_estacoes(sorteios),
            'comportamento_mes_sorte_sazonal': AnaliseSazonalService.analisar_mes_sorte_sazonal(sorteios),
            'tendencias_sazonais': AnaliseSazonalService.identificar_tendencias_sazonais(sorteios)
        }

    @staticmethod
    def obter_trimestre(data_sorteio):
        if isinstance(data_sorteio, str):
            data_sorteio = datetime.strptime(data_sorteio, '%Y-%m-%d')

        mes = data_sorteio.month
        if mes in [1, 2, 3]:
            return 1
        elif mes in [4, 5, 6]:
            return 2
        elif mes in [7, 8, 9]:
            return 3
        else:
            return 4

    @staticmethod
    def obter_semestre(data_sorteio):
        if isinstance(data_sorteio, str):
            data_sorteio = datetime.strptime(data_sorteio, '%Y-%m-%d')

        return 1 if data_sorteio.month <= 6 else 2

    @staticmethod
    def obter_estacao(data_sorteio):
        if isinstance(data_sorteio, str):
            data_sorteio = datetime.strptime(data_sorteio, '%Y-%m-%d')

        mes = data_sorteio.month
        # Estações do hemisfério sul (Brasil)
        if mes in [12, 1, 2]:
            return 'Verão'
        elif mes in [3, 4, 5]:
            return 'Outono'
        elif mes in [6, 7, 8]:
            return 'Inverno'
        else:
            return 'Primavera'

    @staticmethod
    def analisar_trimestres(sorteios):
        dezenas_por_trimestre = defaultdict(lambda: Counter())
        meses_por_trimestre = defaultdict(lambda: Counter())
        total_por_trimestre = Counter()

        for sorteio in sorteios:
            trimestre = AnaliseSazonalService.obter_trimestre(sorteio.data_sorteio)
            total_por_trimestre[trimestre] += 1

            numeros = sorteio.get_posicoes_lista()
            for numero in numeros:
                dezenas_por_trimestre[trimestre][numero] += 1

            meses_por_trimestre[trimestre][sorteio.mes_sorte] += 1

        resultado = []
        for trimestre in [1, 2, 3, 4]:
            nome_trimestre = f"T{trimestre} ({'Jan-Mar' if trimestre == 1 else 'Abr-Jun' if trimestre == 2 else 'Jul-Set' if trimestre == 3 else 'Out-Dez'})"

            top_dezenas = dezenas_por_trimestre[trimestre].most_common(10)
            top_meses = meses_por_trimestre[trimestre].most_common(5)

            resultado.append({
                'trimestre': trimestre,
                'nome': nome_trimestre,
                'total_sorteios': total_por_trimestre[trimestre],
                'top_dezenas': [
                    {
                        'dezena': dez,
                        'frequencia': freq,
                        'percentual': round((freq / (total_por_trimestre[trimestre] * 7) * 100), 2)
                    }
                    for dez, freq in top_dezenas
                ],
                'top_meses': [
                    {
                        'mes': mes,
                        'mes_nome': AnaliseSazonalService.obter_nome_mes(mes),
                        'frequencia': freq,
                        'percentual': round((freq / total_por_trimestre[trimestre] * 100), 2)
                    }
                    for mes, freq in top_meses
                ]
            })

        return resultado

    @staticmethod
    def analisar_semestres(sorteios):
        dezenas_por_semestre = defaultdict(lambda: Counter())
        meses_por_semestre = defaultdict(lambda: Counter())
        total_por_semestre = Counter()

        for sorteio in sorteios:
            semestre = AnaliseSazonalService.obter_semestre(sorteio.data_sorteio)
            total_por_semestre[semestre] += 1

            numeros = sorteio.get_posicoes_lista()
            for numero in numeros:
                dezenas_por_semestre[semestre][numero] += 1

            meses_por_semestre[semestre][sorteio.mes_sorte] += 1

        resultado = []
        for semestre in [1, 2]:
            nome_semestre = f"S{semestre} ({'Jan-Jun' if semestre == 1 else 'Jul-Dez'})"

            top_dezenas = dezenas_por_semestre[semestre].most_common(10)
            top_meses = meses_por_semestre[semestre].most_common(5)

            resultado.append({
                'semestre': semestre,
                'nome': nome_semestre,
                'total_sorteios': total_por_semestre[semestre],
                'top_dezenas': [
                    {
                        'dezena': dez,
                        'frequencia': freq,
                        'percentual': round((freq / (total_por_semestre[semestre] * 7) * 100), 2)
                    }
                    for dez, freq in top_dezenas
                ],
                'top_meses': [
                    {
                        'mes': mes,
                        'mes_nome': AnaliseSazonalService.obter_nome_mes(mes),
                        'frequencia': freq,
                        'percentual': round((freq / total_por_semestre[semestre] * 100), 2)
                    }
                    for mes, freq in top_meses
                ]
            })

        return resultado

    @staticmethod
    def analisar_estacoes(sorteios):
        dezenas_por_estacao = defaultdict(lambda: Counter())
        meses_por_estacao = defaultdict(lambda: Counter())
        total_por_estacao = Counter()

        for sorteio in sorteios:
            estacao = AnaliseSazonalService.obter_estacao(sorteio.data_sorteio)
            total_por_estacao[estacao] += 1

            numeros = sorteio.get_posicoes_lista()
            for numero in numeros:
                dezenas_por_estacao[estacao][numero] += 1

            meses_por_estacao[estacao][sorteio.mes_sorte] += 1

        resultado = []
        for estacao in ['Verão', 'Outono', 'Inverno', 'Primavera']:
            if total_por_estacao[estacao] == 0:
                continue

            top_dezenas = dezenas_por_estacao[estacao].most_common(10)
            top_meses = meses_por_estacao[estacao].most_common(5)

            resultado.append({
                'estacao': estacao,
                'total_sorteios': total_por_estacao[estacao],
                'top_dezenas': [
                    {
                        'dezena': dez,
                        'frequencia': freq,
                        'percentual': round((freq / (total_por_estacao[estacao] * 7) * 100), 2)
                    }
                    for dez, freq in top_dezenas
                ],
                'top_meses': [
                    {
                        'mes': mes,
                        'mes_nome': AnaliseSazonalService.obter_nome_mes(mes),
                        'frequencia': freq,
                        'percentual': round((freq / total_por_estacao[estacao] * 100), 2)
                    }
                    for mes, freq in top_meses
                ]
            })

        return resultado

    @staticmethod
    def analisar_mes_sorte_sazonal(sorteios):
        meses_por_periodo = {
            'Trimestre': defaultdict(lambda: Counter()),
            'Semestre': defaultdict(lambda: Counter()),
            'Estação': defaultdict(lambda: Counter())
        }

        for sorteio in sorteios:
            trimestre = AnaliseSazonalService.obter_trimestre(sorteio.data_sorteio)
            semestre = AnaliseSazonalService.obter_semestre(sorteio.data_sorteio)
            estacao = AnaliseSazonalService.obter_estacao(sorteio.data_sorteio)

            meses_por_periodo['Trimestre'][trimestre][sorteio.mes_sorte] += 1
            meses_por_periodo['Semestre'][semestre][sorteio.mes_sorte] += 1
            meses_por_periodo['Estação'][estacao][sorteio.mes_sorte] += 1

        return {
            'meses_por_trimestre': dict(meses_por_periodo['Trimestre']),
            'meses_por_semestre': dict(meses_por_periodo['Semestre']),
            'meses_por_estacao': dict(meses_por_periodo['Estação'])
        }

    @staticmethod
    def identificar_tendencias_sazonais(sorteios):
        # Identifica padrões que se repetem sazonalmente
        soma_por_trimestre = defaultdict(list)
        pares_por_trimestre = defaultdict(list)

        for sorteio in sorteios:
            trimestre = AnaliseSazonalService.obter_trimestre(sorteio.data_sorteio)
            numeros = sorteio.get_posicoes_lista()

            soma = sum(numeros)
            pares = sum(1 for n in numeros if n % 2 == 0)

            soma_por_trimestre[trimestre].append(soma)
            pares_por_trimestre[trimestre].append(pares)

        resultado = []
        for trimestre in [1, 2, 3, 4]:
            nome_trimestre = f"T{trimestre}"
            somas = soma_por_trimestre[trimestre]
            pares_list = pares_por_trimestre[trimestre]

            if somas:
                resultado.append({
                    'trimestre': trimestre,
                    'nome': nome_trimestre,
                    'soma_media': round(sum(somas) / len(somas), 2),
                    'pares_medio': round(sum(pares_list) / len(pares_list), 2),
                    'total_sorteios': len(somas)
                })

        return resultado

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
