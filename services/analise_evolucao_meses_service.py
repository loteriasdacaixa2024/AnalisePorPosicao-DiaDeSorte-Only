from models.sorteio import Sorteio, db
from collections import defaultdict
from datetime import datetime

class AnaliseEvolucaoMesesService:

    @staticmethod
    def analisar_evolucao_meses():
        sorteios = Sorteio.query.order_by(Sorteio.data_sorteio.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        frequencia_por_mes = defaultdict(int)
        frequencia_por_ano = defaultdict(lambda: defaultdict(int))
        evolucao_temporal = defaultdict(list)

        primeiro_ano = sorteios[0].data_sorteio.year if sorteios[0].data_sorteio else None
        ultimo_ano = sorteios[-1].data_sorteio.year if sorteios[-1].data_sorteio else None

        meses_nomes = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }

        for sorteio in sorteios:
            if sorteio.mes_sorte:
                mes = sorteio.mes_sorte
                frequencia_por_mes[mes] += 1

                if sorteio.data_sorteio:
                    ano = sorteio.data_sorteio.year
                    frequencia_por_ano[ano][mes] += 1

        distribuicao_geral = []
        for mes in range(1, 13):
            freq = frequencia_por_mes[mes]
            percentual = round((freq / total_concursos * 100), 2) if total_concursos > 0 else 0

            distribuicao_geral.append({
                'mes': mes,
                'nome': meses_nomes[mes],
                'frequencia': freq,
                'porcentagem': percentual
            })

        distribuicao_geral.sort(key=lambda x: x['frequencia'], reverse=True)

        evolucao_por_ano = []
        if primeiro_ano and ultimo_ano:
            for ano in range(primeiro_ano, ultimo_ano + 1):
                dados_ano = {
                    'ano': ano,
                    'meses': []
                }

                total_ano = sum(frequencia_por_ano[ano].values())

                for mes in range(1, 13):
                    freq = frequencia_por_ano[ano][mes]
                    perc = round((freq / total_ano * 100), 2) if total_ano > 0 else 0

                    dados_ano['meses'].append({
                        'mes': mes,
                        'nome': meses_nomes[mes],
                        'frequencia': freq,
                        'porcentagem': perc
                    })

                evolucao_por_ano.append(dados_ano)

        meses_quentes = distribuicao_geral[:3]
        meses_frios = distribuicao_geral[-3:]

        tendencias = []
        for mes in range(1, 13):
            frequencias_ano = []
            anos_lista = []

            if primeiro_ano and ultimo_ano:
                for ano in range(primeiro_ano, ultimo_ano + 1):
                    freq = frequencia_por_ano[ano][mes]
                    frequencias_ano.append(freq)
                    anos_lista.append(ano)

            if len(frequencias_ano) >= 2:
                primeira_metade = frequencias_ano[:len(frequencias_ano)//2]
                segunda_metade = frequencias_ano[len(frequencias_ano)//2:]

                media_primeira = sum(primeira_metade) / len(primeira_metade) if primeira_metade else 0
                media_segunda = sum(segunda_metade) / len(segunda_metade) if segunda_metade else 0

                if media_segunda > media_primeira * 1.2:
                    tendencia = 'Crescente'
                elif media_segunda < media_primeira * 0.8:
                    tendencia = 'Decrescente'
                else:
                    tendencia = 'Estável'
            else:
                tendencia = 'Dados insuficientes'

            tendencias.append({
                'mes': mes,
                'nome': meses_nomes[mes],
                'tendencia': tendencia,
                'frequencias': frequencias_ano,
                'anos': anos_lista
            })

        return {
            'total_concursos': total_concursos,
            'primeiro_ano': primeiro_ano,
            'ultimo_ano': ultimo_ano,
            'distribuicao_geral': distribuicao_geral,
            'meses_quentes': meses_quentes,
            'meses_frios': meses_frios,
            'evolucao_por_ano': evolucao_por_ano,
            'tendencias': tendencias
        }