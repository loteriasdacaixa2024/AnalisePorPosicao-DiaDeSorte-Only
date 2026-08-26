from collections import Counter, defaultdict
from models import Sorteio
from sqlalchemy import func


class AnaliseTubularService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {
                'erro': 'Nenhum sorteio encontrado',
                'total_concursos': 0
            }

        sorteios_ordenados = sorted(sorteios, key=lambda x: x.concurso)

        return {
            'total_concursos': len(sorteios_ordenados),
            'sequencias': AnaliseTubularService.analisar_sequencias(sorteios_ordenados),
            'finais': AnaliseTubularService.analisar_finais_iguais(sorteios_ordenados),
            'repeticoes': AnaliseTubularService.analisar_repeticoes(sorteios_ordenados),
            'somas': AnaliseTubularService.analisar_somas(sorteios_ordenados),
            'pares_impares': AnaliseTubularService.analisar_pares_impares(sorteios_ordenados),
            'padroes_iniciais_finais': AnaliseTubularService.analisar_padroes_iniciais_finais(sorteios_ordenados),
            'meses': AnaliseTubularService.analisar_meses_sorte(sorteios_ordenados),
            'digitos_unicos': AnaliseTubularService.analisar_digitos_unicos(sorteios_ordenados)
        }

    @staticmethod
    def obter_numeros_sorteio(sorteio):
        return sorted(sorteio.get_posicoes_lista())

    @staticmethod
    def analisar_sequencias(sorteios):
        seq_2 = 0
        seq_3 = 0
        seq_4_plus = 0
        exemplos_seq_2 = []
        exemplos_seq_3 = []
        exemplos_seq_4 = []

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            seq_atual = 1
            maior_seq = 1

            for i in range(1, len(numeros)):
                if numeros[i] == numeros[i-1] + 1:
                    seq_atual += 1
                    maior_seq = max(maior_seq, seq_atual)
                else:
                    seq_atual = 1

            if maior_seq == 2:
                seq_2 += 1
                if len(exemplos_seq_2) < 3:
                    exemplos_seq_2.append(sorteio.concurso)
            elif maior_seq == 3:
                seq_3 += 1
                if len(exemplos_seq_3) < 3:
                    exemplos_seq_3.append(sorteio.concurso)
            elif maior_seq >= 4:
                seq_4_plus += 1
                if len(exemplos_seq_4) < 3:
                    exemplos_seq_4.append(sorteio.concurso)

        total = len(sorteios)

        padroes = [
            {
                'descricao': 'Sequência de 2',
                'frequencia': seq_2,
                'percentual': round((seq_2 / total) * 100, 2),
                'exemplos': exemplos_seq_2,
                'status': 'MAIS' if seq_2 > (total * 0.3) else 'MENOS' if seq_2 < (total * 0.15) else 'MÉDIA'
            },
            {
                'descricao': 'Sequência de 3',
                'frequencia': seq_3,
                'percentual': round((seq_3 / total) * 100, 2),
                'exemplos': exemplos_seq_3,
                'status': 'MAIS' if seq_3 > (total * 0.2) else 'MENOS' if seq_3 < (total * 0.05) else 'MÉDIA'
            },
            {
                'descricao': 'Sequência de 4+',
                'frequencia': seq_4_plus,
                'percentual': round((seq_4_plus / total) * 100, 2),
                'exemplos': exemplos_seq_4,
                'status': 'MAIS' if seq_4_plus > (total * 0.1) else 'MENOS' if seq_4_plus < (total * 0.02) else 'MÉDIA'
            }
        ]

        return {
            'padroes': sorted(padroes, key=lambda x: x['frequencia'], reverse=True),
            'total': seq_2 + seq_3 + seq_4_plus
        }

    @staticmethod
    def analisar_finais_iguais(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': []})

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            finais_count = Counter([n % 10 for n in numeros])
            max_count = max(finais_count.values())
            final_mais_frequente = [k for k, v in finais_count.items() if v == max_count][0]

            chave = f"{max_count}x final {final_mais_frequente}"
            contadores[chave]['frequencia'] += 1
            if len(contadores[chave]['exemplos']) < 3:
                contadores[chave]['exemplos'].append(sorteio.concurso)
            contadores[chave]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []

        for descricao, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': descricao,
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.15) else 'MENOS' if freq < (total * 0.05) else 'MÉDIA'
            })

        return sorted(padroes, key=lambda x: x['frequencia'], reverse=True)

    @staticmethod
    def analisar_repeticoes(sorteios):
        total_repeticoes = 0
        exemplos = []

        for i in range(1, len(sorteios)):
            atual = set(AnaliseTubularService.obter_numeros_sorteio(sorteios[i]))
            anterior = set(AnaliseTubularService.obter_numeros_sorteio(sorteios[i-1]))

            repeticoes = atual & anterior
            qtde_rep = len(repeticoes)

            if qtde_rep > 0:
                total_repeticoes += 1
                if len(exemplos) < 5:
                    exemplos.append({
                        'concurso': sorteios[i].concurso,
                        'qtde': qtde_rep,
                        'numeros': sorted(list(repeticoes))
                    })

        total = len(sorteios) - 1

        return {
            'total': total_repeticoes,
            'percentual': round((total_repeticoes / total) * 100, 2),
            'exemplos': exemplos,
            'media_repeticoes': round(total_repeticoes / total, 2),
            'status': 'MAIS' if total_repeticoes > (total * 0.5) else 'MENOS' if total_repeticoes < (total * 0.3) else 'MÉDIA'
        }

    @staticmethod
    def analisar_somas(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': []})

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            soma = sum(numeros)

            contadores[soma]['frequencia'] += 1
            if len(contadores[soma]['exemplos']) < 3:
                contadores[soma]['exemplos'].append(sorteio.concurso)
            contadores[soma]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []
        somas_valores = list(contadores.keys())
        media_soma = round(sum(somas_valores) / len(somas_valores), 1)

        for soma, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': f'Soma {soma}',
                'soma': soma,
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.1) else 'MENOS' if freq < (total * 0.02) else 'MÉDIA'
            })

        return {
            'padroes': sorted(padroes, key=lambda x: x['frequencia'], reverse=True)[:10],
            'media_soma': media_soma
        }

    @staticmethod
    def analisar_pares_impares(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': []})

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = 7 - pares

            descricao = f"{pares}P + {impares}I"
            contadores[descricao]['frequencia'] += 1
            contadores[descricao]['pares'] = pares
            contadores[descricao]['impares'] = impares
            if len(contadores[descricao]['exemplos']) < 3:
                contadores[descricao]['exemplos'].append(sorteio.concurso)
            contadores[descricao]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []

        for descricao, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': descricao,
                'pares': dados['pares'],
                'impares': dados['impares'],
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.15) else 'MENOS' if freq < (total * 0.05) else 'MÉDIA'
            })

        return sorted(padroes, key=lambda x: x['frequencia'], reverse=True)

    @staticmethod
    def analisar_padroes_iniciais_finais(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': []})

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            inicial = numeros[0]
            final = numeros[-1]

            faixa_inicial = "01-10" if inicial <= 10 else "11-20" if inicial <= 20 else "21-31"
            faixa_final = "01-10" if final <= 10 else "11-20" if final <= 20 else "21-31"

            descricao = f"Inicial: {faixa_inicial} / Final: {faixa_final}"
            contadores[descricao]['frequencia'] += 1
            if len(contadores[descricao]['exemplos']) < 3:
                contadores[descricao]['exemplos'].append(sorteio.concurso)
            contadores[descricao]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []

        for descricao, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': descricao,
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.15) else 'MENOS' if freq < (total * 0.05) else 'MÉDIA'
            })

        return sorted(padroes, key=lambda x: x['frequencia'], reverse=True)

    @staticmethod
    def analisar_meses_sorte(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': []})

        for sorteio in sorteios:
            mes = sorteio.get_nome_mes()

            contadores[mes]['frequencia'] += 1
            contadores[mes]['mes_numero'] = sorteio.mes_sorte
            if len(contadores[mes]['exemplos']) < 3:
                contadores[mes]['exemplos'].append(sorteio.concurso)
            contadores[mes]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []

        for mes, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': mes,
                'mes_numero': dados['mes_numero'],
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.1) else 'MENOS' if freq < (total * 0.06) else 'MÉDIA'
            })

        return sorted(padroes, key=lambda x: x['frequencia'], reverse=True)

    @staticmethod
    def analisar_digitos_unicos(sorteios):
        contadores = defaultdict(lambda: {'frequencia': 0, 'exemplos': [], 'ultimos': [], 'numeros_exemplo': []})

        for sorteio in sorteios:
            numeros = AnaliseTubularService.obter_numeros_sorteio(sorteio)
            digitos = set()
            for n in numeros:
                digitos.update(str(n))

            qtde_digitos = len(digitos)

            contadores[qtde_digitos]['frequencia'] += 1
            if len(contadores[qtde_digitos]['exemplos']) < 3:
                contadores[qtde_digitos]['exemplos'].append(sorteio.concurso)
                contadores[qtde_digitos]['numeros_exemplo'].append(numeros)
            contadores[qtde_digitos]['ultimos'] = [sorteio.concurso]

        total = len(sorteios)
        padroes = []

        for qtde, dados in contadores.items():
            freq = dados['frequencia']
            padroes.append({
                'descricao': f'{qtde} dígitos únicos',
                'qtde': qtde,
                'frequencia': freq,
                'percentual': round((freq / total) * 100, 2),
                'exemplos': dados['exemplos'],
                'numeros_exemplo': dados['numeros_exemplo'][0] if dados['numeros_exemplo'] else [],
                'ultimo_concurso': dados['ultimos'][-1] if dados['ultimos'] else 0,
                'atraso': sorteios[-1].concurso - dados['ultimos'][-1] if dados['ultimos'] else 0,
                'status': 'MAIS' if freq > (total * 0.15) else 'MENOS' if freq < (total * 0.05) else 'MÉDIA'
            })

        return sorted(padroes, key=lambda x: x['frequencia'], reverse=True)
