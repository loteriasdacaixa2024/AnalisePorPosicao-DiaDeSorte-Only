from models.sorteio import Sorteio, db
from collections import defaultdict

class AnaliseDigitosUnicosService:

    @staticmethod
    def analisar_digitos_unicos():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'error': 'Nenhum sorteio encontrado'}

        total_concursos = len(sorteios)
        
        frequencia_quantidade_digitos = defaultdict(int)
        combinacoes_digitos = defaultdict(list)
        frequencia_relacao_digitos_soma = defaultdict(int)
        concursos_por_relacao = defaultdict(list)
        
        quantidade_minima = 10
        quantidade_maxima = 0
        soma_quantidades = 0

        for sorteio in sorteios:
            numeros = []
            digitos_unicos = set()

            for posicao in range(1, 8):
                numero = getattr(sorteio, f'posicao_{posicao}')
                if numero:
                    numeros.append(numero)
                    dezena = numero // 10
                    unidade = numero % 10
                    digitos_unicos.add(dezena)
                    digitos_unicos.add(unidade)

            quantidade = len(digitos_unicos)
            frequencia_quantidade_digitos[quantidade] += 1
            
            soma_dezenas = sum(numeros)
            relacao = f"{quantidade}/{soma_dezenas}"
            frequencia_relacao_digitos_soma[relacao] += 1
            concursos_por_relacao[relacao].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': [f"{n:02d}" for n in sorted(numeros)]
            })
            
            soma_quantidades += quantidade
            
            if quantidade < quantidade_minima:
                quantidade_minima = quantidade
            if quantidade > quantidade_maxima:
                quantidade_maxima = quantidade

            digitos_ordenados = tuple(sorted(digitos_unicos))
            combinacoes_digitos[digitos_ordenados].append({
                'concurso': sorteio.concurso,
                'data': sorteio.data_sorteio.strftime('%d/%m/%Y') if sorteio.data_sorteio else '',
                'numeros': sorted(numeros),
                'digitos': list(digitos_ordenados)
            })

        media_quantidade = round(soma_quantidades / total_concursos, 2)

        analise_por_quantidade = []
        for quantidade in sorted(frequencia_quantidade_digitos.keys()):
            freq = frequencia_quantidade_digitos[quantidade]
            percentual = round((freq / total_concursos * 100), 2)
            
            analise_por_quantidade.append({
                'quantidade': quantidade,
                'frequencia': freq,
                'porcentagem': percentual
            })

        frequencia_combinacoes = {combo: len(concursos) for combo, concursos in combinacoes_digitos.items()}
        top_combinacoes = sorted(frequencia_combinacoes.items(), key=lambda x: x[1], reverse=True)[:10]

        combinacoes_formatadas = []
        for combinacao, freq in top_combinacoes:
            digitos_str = ', '.join([str(d) for d in combinacao])
            percentual = round((freq / total_concursos * 100), 2)
            combinacoes_formatadas.append({
                'digitos': list(combinacao),
                'digitos_str': digitos_str,
                'quantidade': len(combinacao),
                'frequencia': freq,
                'porcentagem': percentual,
                'concursos': combinacoes_digitos[combinacao]
            })

        top_relacoes_ordenadas = sorted(frequencia_relacao_digitos_soma.items(), key=lambda x: x[1], reverse=True)
        relacoes_formatadas = []
        for relacao, freq in top_relacoes_ordenadas:
            percentual = round((freq / total_concursos * 100), 2)
            relacoes_formatadas.append({
                'relacao': relacao,
                'frequencia': freq,
                'porcentagem': percentual,
                'concursos': concursos_por_relacao[relacao]
            })

        return {
            'total_concursos': total_concursos,
            'quantidade_minima': quantidade_minima,
            'quantidade_maxima': quantidade_maxima,
            'quantidade_media': media_quantidade,
            'analise_por_quantidade': analise_por_quantidade,
            'top_combinacoes': combinacoes_formatadas,
            'top_relacoes_soma': relacoes_formatadas
        }

    @staticmethod
    def gerar_matriz_elite(relacoes_alvo):
        """
        Vareja as 2.6M de combinações numa única varredura.
        Filtra apenas combinações de Ouro (Pares entre 2..5 e Sequências <= 3).
        Retorna no máximo 300 exemplos por Relação (para economizar payload), 
        assegurando que cumprem os rigores de 7 dígitos / Soma X.
        """
        import time
        import random
        from itertools import combinations
        
        # Converte as strings ['7/104', '7/117'] num dict de Sets
        alvos = set(relacoes_alvo)
        matriz = { r: [] for r in alvos }
        
        # A varredura de ouro
        for combo in combinations(range(1, 32), 7):
            soma = sum(combo)
            digs = set()
            for x in combo:
                digs.add(x // 10)
                digs.add(x % 10)
            
            chave = f"{len(digs)}/{soma}"
            if chave in alvos:
                # Extrator de Filtros Inéditos
                pares = sum(1 for x in combo if x % 2 == 0)
                if 2 <= pares <= 5: # Máximo equilíbrio de ímpares e pares (nada bizarro como 7 pares)
                    max_seq = 1
                    curr_seq = 1
                    for i in range(1, 7):
                        if combo[i] == combo[i-1] + 1:
                            curr_seq += 1
                            if curr_seq > max_seq: max_seq = curr_seq
                        else:
                            curr_seq = 1
                    
                    if max_seq <= 3: # Sem sequências longas viciadas
                        matriz[chave].append(combo)

        # Apenas embaralha a matriz mas devolve a quantidade INTACTA E REAL do filtro
        for k in matriz.keys():
            random.shuffle(matriz[k])
            
        return matriz

