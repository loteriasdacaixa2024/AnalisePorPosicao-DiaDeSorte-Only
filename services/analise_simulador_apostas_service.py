from models.sorteio import Sorteio, db
from collections import defaultdict


class AnaliseSimuladorApostasService:

    @staticmethod
    def simular_aposta(numeros_apostados, mes_aposta, concursos_limite=None):
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        if not numeros_apostados or len(numeros_apostados) != 7:
            return {'error': 'Você deve fornecer exatamente 7 números'}

        if mes_aposta < 1 or mes_aposta > 12:
            return {'error': 'Mês da sorte deve estar entre 1 e 12'}

        numeros_set = set(numeros_apostados)
        if len(numeros_set) != 7:
            return {'error': 'Os 7 números devem ser diferentes'}

        for num in numeros_apostados:
            if num < 1 or num > 31:
                return {'error': 'Todos os números devem estar entre 1 e 31'}

        if concursos_limite:
            sorteios = sorteios[:concursos_limite]

        total_concursos = len(sorteios)
        resultados = []
        acertos_por_quantidade = {i: 0 for i in range(8)}
        acertos_mes = 0
        total_acertos_numeros = 0
        melhor_resultado = None
        pior_resultado = None
        concursos_com_acerto = 0
        concursos_sem_acerto = 0

        for sorteio in sorteios:
            numeros_sorteio = {getattr(sorteio, f'posicao_{i}') for i in range(1, 8) if getattr(sorteio, f'posicao_{i}')}

            acertos = numeros_set & numeros_sorteio
            quantidade_acertos = len(acertos)
            acerto_mes = sorteio.mes_sorte == mes_aposta

            if acerto_mes:
                acertos_mes += 1

            acertos_por_quantidade[quantidade_acertos] += 1
            total_acertos_numeros += quantidade_acertos

            if quantidade_acertos > 0:
                concursos_com_acerto += 1
            else:
                concursos_sem_acerto += 1

            # Estimativa simples de prêmio (pode ser ajustada conforme regras reais)
            premio_estimado = 0
            if quantidade_acertos == 7 and acerto_mes:
                premio_estimado = 1_000_000
            elif quantidade_acertos == 7:
                premio_estimado = 50_000
            elif quantidade_acertos == 6 and acerto_mes:
                premio_estimado = 5_000
            elif quantidade_acertos == 6:
                premio_estimado = 1_000
            elif quantidade_acertos == 5 and acerto_mes:
                premio_estimado = 500
            elif quantidade_acertos == 5:
                premio_estimado = 100
            elif quantidade_acertos == 4 and acerto_mes:
                premio_estimado = 50
            elif quantidade_acertos == 4:
                premio_estimado = 10

            resultado_concurso = {
                'concurso': sorteio.concurso,
                'numeros_sorteio': sorted(numeros_sorteio),
                'mes_sorteio': sorteio.mes_sorte,
                'acertos': sorted(acertos),
                'quantidade_acertos': quantidade_acertos,
                'acerto_mes': acerto_mes,
                'premio_estimado': premio_estimado,
            }

            resultados.append(resultado_concurso)

            if melhor_resultado is None or quantidade_acertos > melhor_resultado['quantidade_acertos']:
                melhor_resultado = resultado_concurso
            if pior_resultado is None or quantidade_acertos < pior_resultado['quantidade_acertos']:
                pior_resultado = resultado_concurso

        media_acertos = total_acertos_numeros / total_concursos if total_concursos else 0
        percentual_acertos = {
            k: round(v / total_concursos * 100, 2) if total_concursos else 0
            for k, v in acertos_por_quantidade.items()
        }

        premio_total = sum(r['premio_estimado'] for r in resultados)
        custo_total = total_concursos * 2.5
        lucro_liquido = premio_total - custo_total

        taxa_acerto = round(concursos_com_acerto / total_concursos * 100, 2) if total_concursos else 0
        taxa_acerto_mes = round(acertos_mes / total_concursos * 100, 2) if total_concursos else 0

        return {
            'numeros_apostados': sorted(numeros_apostados),
            'mes_aposta': mes_aposta,
            'total_concursos': total_concursos,
            'resultados': resultados[-10:],  # últimos 10
            'acertos_por_quantidade': acertos_por_quantidade,
            'percentual_acertos': percentual_acertos,
            'media_acertos': round(media_acertos, 2),
            'acertos_mes': acertos_mes,
            'taxa_acerto_mes': taxa_acerto_mes,
            'melhor_resultado': melhor_resultado,
            'pior_resultado': pior_resultado,
            'concursos_com_acerto': concursos_com_acerto,
            'concursos_sem_acerto': concursos_sem_acerto,
            'taxa_acerto': taxa_acerto,
            'premio_total': premio_total,
            'custo_total': custo_total,
            'lucro_liquido': lucro_liquido,
        }
