from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseEspelhadosService:

    @staticmethod
    def obter_espelhado(numero):
        if numero < 10:
            return None

        dezena = numero // 10
        unidade = numero % 10

        espelhado = unidade * 10 + dezena

        if 1 <= espelhado <= 31:
            return espelhado
        return None

    @staticmethod
    def analisar_espelhados():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        ultimo_concurso = sorteios[0].concurso

        pares_espelhados_possiveis = {}
        for num in range(10, 32):
            esp = AnaliseEspelhadosService.obter_espelhado(num)
            if esp and esp != num and esp >= 10:
                par = tuple(sorted([num, esp]))
                if par not in pares_espelhados_possiveis:
                    pares_espelhados_possiveis[par] = 0

        frequencia_pares = defaultdict(int)
        ultimo_aparecimento_par = defaultdict(int)

        sorteios_com_espelhados = 0
        sorteios_sem_espelhados = 0

        detalhes_sorteios = []

        for sorteio in sorteios:
            numeros = []

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            pares_encontrados = []
            tem_espelhado = False

            for i in range(len(numeros)):
                for j in range(i + 1, len(numeros)):
                    n1 = numeros[i]
                    n2 = numeros[j]

                    esp_n1 = AnaliseEspelhadosService.obter_espelhado(n1)
                    esp_n2 = AnaliseEspelhadosService.obter_espelhado(n2)

                    if esp_n1 == n2 or esp_n2 == n1:
                        par = tuple(sorted([n1, n2]))
                        pares_encontrados.append(f"{par[0]}-{par[1]}")
                        frequencia_pares[par] += 1
                        ultimo_aparecimento_par[par] = sorteio.concurso
                        tem_espelhado = True

            if tem_espelhado:
                sorteios_com_espelhados += 1
            else:
                sorteios_sem_espelhados += 1

            if pares_encontrados:
                detalhes_sorteios.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': sorted(numeros),
                    'pares_espelhados': pares_encontrados
                })

        percentual_com_espelhados = round((sorteios_com_espelhados / total_concursos * 100), 2)
        percentual_sem_espelhados = round((sorteios_sem_espelhados / total_concursos * 100), 2)

        top_pares = []
        for par, freq in sorted(frequencia_pares.items(), key=lambda x: x[1], reverse=True):
            percentual = round((freq / total_concursos * 100), 2)
            atraso = ultimo_concurso - ultimo_aparecimento_par[par]

            top_pares.append({
                'par': f"{par[0]}-{par[1]}",
                'numero1': par[0],
                'numero2': par[1],
                'frequencia': freq,
                'porcentagem': percentual,
                'ultimo_concurso': ultimo_aparecimento_par[par],
                'atraso': atraso
            })

        todos_pares_possiveis = []
        for par in pares_espelhados_possiveis.keys():
            freq = frequencia_pares.get(par, 0)
            if freq > 0:
                percentual = round((freq / total_concursos * 100), 2)
                atraso = ultimo_concurso - ultimo_aparecimento_par.get(par, 0)
            else:
                percentual = 0.0
                atraso = ultimo_concurso

            todos_pares_possiveis.append({
                'par': f"{par[0]}-{par[1]}",
                'numero1': par[0],
                'numero2': par[1],
                'frequencia': freq,
                'porcentagem': percentual,
                'ultimo_concurso': ultimo_aparecimento_par.get(par, 0),
                'atraso': atraso
            })

        todos_pares_possiveis.sort(key=lambda x: x['frequencia'], reverse=True)

        return {
            'total_concursos': total_concursos,
            'sorteios_com_espelhados': sorteios_com_espelhados,
            'percentual_com_espelhados': percentual_com_espelhados,
            'sorteios_sem_espelhados': sorteios_sem_espelhados,
            'percentual_sem_espelhados': percentual_sem_espelhados,
            'total_pares_encontrados': len(frequencia_pares),
            'top_pares': top_pares,
            'todos_pares': todos_pares_possiveis,
            'detalhes_sorteios': detalhes_sorteios[:100]
        }