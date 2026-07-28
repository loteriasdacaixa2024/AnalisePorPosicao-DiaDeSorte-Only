from models.sorteio import Sorteio, db
from collections import defaultdict, Counter
import statistics

class AnaliseGapsService:

    @staticmethod
    def analisar_gaps():
        """
        Análise completa e profissional de gaps (distâncias entre números consecutivos).
        Retorna estatísticas detalhadas, distribuições e insights.
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        # Estruturas para análise
        frequencia_gaps = defaultdict(int)
        todos_gaps = []  # Lista de TODOS os gaps para cálculos estatísticos
        gap_minimo_geral = 100
        gap_maximo_geral = 0
        soma_gap_minimo = 0
        soma_gap_maximo = 0
        soma_gap_medio = 0

        # Análise de padrões de distribuição
        sorteios_com_gaps_pequenos = 0  # 1-3
        sorteios_com_gaps_medios = 0    # 4-7
        sorteios_com_gaps_grandes = 0   # 8+

        detalhes_sorteios = []

        print(f"📊 Iniciando análise de gaps para {total_concursos} sorteios...")

        for sorteio in sorteios:
            numeros = []

            # Coletar todos os números do sorteio
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            numeros_ordenados = sorted(numeros)

            # Calcular gaps entre números consecutivos
            gaps = []
            gaps_detalhados = []  # Para mostrar no tooltip/detalhes

            for i in range(len(numeros_ordenados) - 1):
                gap = numeros_ordenados[i + 1] - numeros_ordenados[i]
                gaps.append(gap)
                gaps_detalhados.append({
                    'de': numeros_ordenados[i],
                    'para': numeros_ordenados[i + 1],
                    'gap': gap
                })
                frequencia_gaps[gap] += 1
                todos_gaps.append(gap)

            if gaps:
                gap_min = min(gaps)
                gap_max = max(gaps)
                gap_medio = round(sum(gaps) / len(gaps), 2)
                soma_gaps = sum(gaps)

                # Contar tipos de gaps neste sorteio
                gaps_pequenos = len([g for g in gaps if 1 <= g <= 3])
                gaps_medios = len([g for g in gaps if 4 <= g <= 7])
                gaps_grandes = len([g for g in gaps if g >= 8])

                # Classificação do sorteio baseado em distribuição de gaps
                if gaps_pequenos >= 4:
                    sorteios_com_gaps_pequenos += 1
                if gaps_medios >= 3:
                    sorteios_com_gaps_medios += 1
                if gaps_grandes >= 2:
                    sorteios_com_gaps_grandes += 1

                soma_gap_minimo += gap_min
                soma_gap_maximo += gap_max
                soma_gap_medio += gap_medio

                if gap_min < gap_minimo_geral:
                    gap_minimo_geral = gap_min
                if gap_max > gap_maximo_geral:
                    gap_maximo_geral = gap_max

                # Determinar mês da sorte (se disponível)
                mes_sorte = sorteio.mes_sorte if hasattr(sorteio, 'mes_sorte') and sorteio.mes_sorte else None

                detalhes_sorteios.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': numeros_ordenados,
                    'mes_sorte': mes_sorte,
                    'gaps': gaps,
                    'gaps_detalhados': gaps_detalhados,
                    'gap_minimo': gap_min,
                    'gap_maximo': gap_max,
                    'gap_medio': gap_medio,
                    'soma_gaps': soma_gaps,
                    'gaps_pequenos': gaps_pequenos,
                    'gaps_medios': gaps_medios,
                    'gaps_grandes': gaps_grandes,
                    # Classificação visual
                    'classificacao': AnaliseGapsService._classificar_distribuicao(
                        gaps_pequenos, gaps_medios, gaps_grandes
                    )
                })

        # Cálculos estatísticos GERAIS
        media_gap_minimo = round(soma_gap_minimo / total_concursos, 2)
        media_gap_maximo = round(soma_gap_maximo / total_concursos, 2)
        media_gap_medio = round(soma_gap_medio / total_concursos, 2)

        # Estatísticas avançadas usando TODOS os gaps
        mediana_gaps = round(statistics.median(todos_gaps), 2)
        moda_gaps = Counter(todos_gaps).most_common(1)[0][0] if todos_gaps else 0
        desvio_padrao_gaps = round(statistics.stdev(todos_gaps), 2) if len(todos_gaps) > 1 else 0

        # Quartis
        q1 = round(statistics.quantiles(todos_gaps, n=4)[0], 2) if len(todos_gaps) >= 4 else 0
        q3 = round(statistics.quantiles(todos_gaps, n=4)[2], 2) if len(todos_gaps) >= 4 else 0

        # Distribuição de gaps
        distribuicao_gaps = []
        total_gaps_count = sum(frequencia_gaps.values())

        for gap in sorted(frequencia_gaps.keys()):
            freq = frequencia_gaps[gap]
            percentual = round((freq / total_gaps_count * 100), 2)

            distribuicao_gaps.append({
                'gap': gap,
                'frequencia': freq,
                'porcentagem': percentual
            })

        # Top gaps mais frequentes
        top_gaps = sorted(distribuicao_gaps, key=lambda x: x['frequencia'], reverse=True)[:10]

        # Análise de padrões
        perc_pequenos = round((sorteios_com_gaps_pequenos / total_concursos) * 100, 2)
        perc_medios = round((sorteios_com_gaps_medios / total_concursos) * 100, 2)
        perc_grandes = round((sorteios_com_gaps_grandes / total_concursos) * 100, 2)

        print(f"✅ Análise concluída: {total_concursos} sorteios, {len(todos_gaps)} gaps analisados")

        return {
            'total_concursos': total_concursos,
            'total_gaps_analisados': len(todos_gaps),

            # Estatísticas básicas
            'gap_minimo_geral': gap_minimo_geral,
            'gap_maximo_geral': gap_maximo_geral,
            'media_gap_minimo': media_gap_minimo,
            'media_gap_maximo': media_gap_maximo,
            'media_gap_medio': media_gap_medio,

            # Estatísticas avançadas
            'mediana_gaps': mediana_gaps,
            'moda_gaps': moda_gaps,
            'desvio_padrao_gaps': desvio_padrao_gaps,
            'quartil_1': q1,
            'quartil_3': q3,

            # Distribuições
            'distribuicao_gaps': distribuicao_gaps,
            'top_gaps': top_gaps,

            # Padrões de distribuição
            'padroes': {
                'sorteios_gaps_pequenos': sorteios_com_gaps_pequenos,
                'sorteios_gaps_medios': sorteios_com_gaps_medios,
                'sorteios_gaps_grandes': sorteios_com_gaps_grandes,
                'perc_gaps_pequenos': perc_pequenos,
                'perc_gaps_medios': perc_medios,
                'perc_gaps_grandes': perc_grandes
            },

            # TODOS os sorteios com detalhes
            'detalhes_sorteios': detalhes_sorteios  # SEM LIMITE - mostrar todos!
        }

    @staticmethod
    def _classificar_distribuicao(pequenos, medios, grandes):
        """
        Classifica a distribuição de gaps em um sorteio.
        Retorna: 'equilibrado', 'concentrado_pequenos', 'concentrado_medios',
                 'concentrado_grandes', 'misto'
        """
        total = pequenos + medios + grandes

        if total == 0:
            return 'indefinido'

        # Percentuais
        perc_pequenos = (pequenos / total) * 100
        perc_medios = (medios / total) * 100
        perc_grandes = (grandes / total) * 100

        # Classificação
        if perc_pequenos >= 60:
            return 'concentrado_pequenos'
        elif perc_grandes >= 40:
            return 'concentrado_grandes'
        elif perc_medios >= 50:
            return 'concentrado_medios'
        elif abs(perc_pequenos - perc_medios) <= 20 and abs(perc_pequenos - perc_grandes) <= 20:
            return 'equilibrado'
        else:
            return 'misto'
