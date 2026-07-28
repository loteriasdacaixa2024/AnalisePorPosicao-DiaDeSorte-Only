from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseConsecutivosService:

    @staticmethod
    def analisar_consecutivos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        frequencia_quantidade_consecutivos = defaultdict(int)
        pares_consecutivos_encontrados = defaultdict(int)
        ultimo_aparecimento_par = defaultdict(int)

        soma_quantidade = 0
        quantidade_minima = 7
        quantidade_maxima = 0

        detalhes_sorteios = []

        for sorteio in sorteios:
            numeros = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            numeros_ordenados = sorted(numeros)

            pares_consecutivos = []
            quantidade_consecutivos = 0

            for i in range(len(numeros_ordenados) - 1):
                if numeros_ordenados[i + 1] - numeros_ordenados[i] == 1:
                    par = f"{numeros_ordenados[i]}-{numeros_ordenados[i + 1]}"
                    pares_consecutivos.append(par)
                    quantidade_consecutivos += 1

                    pares_consecutivos_encontrados[par] += 1
                    ultimo_aparecimento_par[par] = sorteio.concurso

            frequencia_quantidade_consecutivos[quantidade_consecutivos] += 1
            soma_quantidade += quantidade_consecutivos

            if quantidade_consecutivos < quantidade_minima:
                quantidade_minima = quantidade_consecutivos
            if quantidade_consecutivos > quantidade_maxima:
                quantidade_maxima = quantidade_consecutivos

            detalhes_sorteios.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': numeros_ordenados,
                'pares_consecutivos': pares_consecutivos,
                'quantidade': quantidade_consecutivos
            })

        media_quantidade = round(soma_quantidade / total_concursos, 2)

        distribuicao_quantidade = []
        for qtd in sorted(frequencia_quantidade_consecutivos.keys()):
            freq = frequencia_quantidade_consecutivos[qtd]
            percentual = round((freq / total_concursos * 100), 2)

            distribuicao_quantidade.append({
                'quantidade': qtd,
                'frequencia': freq,
                'porcentagem': percentual
            })

        top_pares = []
        for par, freq in sorted(pares_consecutivos_encontrados.items(), key=lambda x: x[1], reverse=True)[:20]:
            percentual = round((freq / total_concursos * 100), 2)
            atraso = ultimo_concurso - ultimo_aparecimento_par[par]

            top_pares.append({
                'par': par,
                'frequencia': freq,
                'porcentagem': percentual,
                'ultimo_concurso': ultimo_aparecimento_par[par],
                'atraso': atraso
            })

        sorteios_com_consecutivos = sum(1 for qtd, freq in frequencia_quantidade_consecutivos.items() if qtd > 0 for _ in range(freq))
        percentual_com_consecutivos = round((sorteios_com_consecutivos / total_concursos * 100), 2)

        sorteios_sem_consecutivos = frequencia_quantidade_consecutivos.get(0, 0)
        percentual_sem_consecutivos = round((sorteios_sem_consecutivos / total_concursos * 100), 2)

        return {
            'total_concursos': total_concursos,
            'quantidade_minima': quantidade_minima,
            'quantidade_maxima': quantidade_maxima,
            'media_quantidade': media_quantidade,
            'sorteios_com_consecutivos': sorteios_com_consecutivos,
            'percentual_com_consecutivos': percentual_com_consecutivos,
            'sorteios_sem_consecutivos': sorteios_sem_consecutivos,
            'percentual_sem_consecutivos': percentual_sem_consecutivos,
            'distribuicao_quantidade': distribuicao_quantidade,
            'top_pares': top_pares,
            'detalhes_sorteios': detalhes_sorteios[:100]
        }