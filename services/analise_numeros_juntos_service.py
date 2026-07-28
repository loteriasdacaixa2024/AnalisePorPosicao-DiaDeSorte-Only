from models.sorteio import Sorteio, db
from collections import defaultdict, Counter
from itertools import combinations

class AnaliseNumerosJuntosService:

    @staticmethod
    def analisar_numeros_juntos():
        """
        Análise completa de números que aparecem juntos nos sorteios.
        Identifica pares, trios e padrões de co-ocorrência.
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)

        # Estruturas para análise de PARES
        frequencia_pares = defaultdict(int)
        detalhes_pares = defaultdict(list)  # Armazena em quais concursos cada par apareceu

        # Estruturas para análise de TRIOS
        frequencia_trios = defaultdict(int)
        detalhes_trios = defaultdict(list)

        # Frequência individual de cada número
        frequencia_numeros = defaultdict(int)

        # Detalhes de cada sorteio
        detalhes_sorteios = []

        print(f"📊 Iniciando análise de números juntos para {total_concursos} sorteios...")

        for sorteio in sorteios:
            numeros = []

            # Coletar todos os números do sorteio
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
                    frequencia_numeros[numero] += 1

            numeros_ordenados = sorted(numeros)

            # Gerar todos os PARES possíveis (combinações de 2)
            pares_no_sorteio = []
            for par in combinations(numeros_ordenados, 2):
                par_ordenado = tuple(sorted(par))
                frequencia_pares[par_ordenado] += 1
                detalhes_pares[par_ordenado].append(sorteio.concurso)
                pares_no_sorteio.append(par_ordenado)

            # Gerar todos os TRIOS possíveis (combinações de 3)
            trios_no_sorteio = []
            for trio in combinations(numeros_ordenados, 3):
                trio_ordenado = tuple(sorted(trio))
                frequencia_trios[trio_ordenado] += 1
                detalhes_trios[trio_ordenado].append(sorteio.concurso)
                trios_no_sorteio.append(trio_ordenado)

            # Determinar mês da sorte
            mes_sorte = sorteio.mes_sorte if hasattr(sorteio, 'mes_sorte') and sorteio.mes_sorte else None

            detalhes_sorteios.append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': numeros_ordenados,
                'mes_sorte': mes_sorte,
                'total_pares': len(pares_no_sorteio),
                'total_trios': len(trios_no_sorteio)
            })

        # Processar TOP pares mais frequentes
        pares_ordenados = sorted(frequencia_pares.items(), key=lambda x: x[1], reverse=True)
        top_pares = []

        for par, freq in pares_ordenados[:100]:  # Top 100 pares
            # Calcular percentual
            percentual = round((freq / total_concursos) * 100, 2)

            # Obter frequência individual de cada número do par
            freq_n1 = frequencia_numeros[par[0]]
            freq_n2 = frequencia_numeros[par[1]]

            # Taxa de correlação: quantas vezes aparecem juntos vs. separados
            taxa_correlacao = round((freq / min(freq_n1, freq_n2)) * 100, 2)

            top_pares.append({
                'numeros': list(par),
                'frequencia': freq,
                'percentual': percentual,
                'taxa_correlacao': taxa_correlacao,
                'concursos': detalhes_pares[par][:10],  # Primeiros 10 concursos
                'total_concursos': len(detalhes_pares[par])
            })

        # Processar TOP trios mais frequentes
        trios_ordenados = sorted(frequencia_trios.items(), key=lambda x: x[1], reverse=True)
        top_trios = []

        for trio, freq in trios_ordenados[:50]:  # Top 50 trios
            percentual = round((freq / total_concursos) * 100, 2)

            top_trios.append({
                'numeros': list(trio),
                'frequencia': freq,
                'percentual': percentual,
                'concursos': detalhes_trios[trio][:10],
                'total_concursos': len(detalhes_trios[trio])
            })

        # Estatísticas gerais
        media_freq_pares = round(sum(frequencia_pares.values()) / len(frequencia_pares), 2) if frequencia_pares else 0
        media_freq_trios = round(sum(frequencia_trios.values()) / len(frequencia_trios), 2) if frequencia_trios else 0

        # Pares e trios mais raros (frequência = 1)
        pares_raros = sum(1 for freq in frequencia_pares.values() if freq == 1)
        trios_raros = sum(1 for freq in frequencia_trios.values() if freq == 1)

        # Números mais "sociáveis" (que aparecem em mais pares diferentes)
        sociabilidade_numeros = defaultdict(set)
        for par in frequencia_pares.keys():
            sociabilidade_numeros[par[0]].add(par[1])
            sociabilidade_numeros[par[1]].add(par[0])

        numeros_sociáveis = sorted(
            [(num, len(parceiros)) for num, parceiros in sociabilidade_numeros.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]

        print(f"✅ Análise concluída: {len(top_pares)} pares, {len(top_trios)} trios analisados")

        return {
            'total_concursos': total_concursos,
            'total_pares_unicos': len(frequencia_pares),
            'total_trios_unicos': len(frequencia_trios),

            # Estatísticas
            'media_freq_pares': media_freq_pares,
            'media_freq_trios': media_freq_trios,
            'pares_raros': pares_raros,
            'trios_raros': trios_raros,

            # Rankings
            'top_pares': top_pares,
            'top_trios': top_trios,
            'numeros_sociaveis': [{'numero': n, 'parceiros': p} for n, p in numeros_sociáveis],

            # Detalhes
            'detalhes_sorteios': detalhes_sorteios
        }

    @staticmethod
    def buscar_par_especifico(numero1, numero2):
        """
        Busca detalhada de um par específico de números.
        Retorna todos os concursos onde esse par apareceu junto.
        """
        sorteios = Sorteio.query.order_by(Sorteio.concurso.desc()).all()

        concursos_com_par = []

        for sorteio in sorteios:
            numeros = []
            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)

            if numero1 in numeros and numero2 in numeros:
                concursos_com_par.append({
                    'concurso': sorteio.concurso,
                    'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                    'numeros': sorted(numeros)
                })

        return {
            'par': [numero1, numero2],
            'total_aparicoes': len(concursos_com_par),
            'concursos': concursos_com_par
        }
