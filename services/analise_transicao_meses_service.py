from collections import defaultdict
from models import Sorteio


class AnaliseTransicaoMesesService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if len(sorteios) < 2:
            return {'erro': 'Dados insuficientes para análise', 'total_concursos': len(sorteios)}

        return {
            'total_concursos': len(sorteios),
            'matriz_transicao': AnaliseTransicaoMesesService.calcular_matriz_transicao(sorteios),
            'sequencias_comuns': AnaliseTransicaoMesesService.identificar_sequencias_comuns(sorteios),
            'mes_mais_persistente': AnaliseTransicaoMesesService.analisar_persistencia(sorteios),
            'probabilidades_proxima': AnaliseTransicaoMesesService.calcular_probabilidades_proxima(sorteios)
        }

    @staticmethod
    def calcular_matriz_transicao(sorteios):
        transicoes = defaultdict(lambda: defaultdict(int))

        for i in range(len(sorteios) - 1):
            mes_atual = sorteios[i].mes_sorte
            mes_seguinte = sorteios[i + 1].mes_sorte
            transicoes[mes_atual][mes_seguinte] += 1

        matriz = []
        for mes_origem in range(1, 13):
            linha = {
                'mes_origem': mes_origem,
                'mes_nome': AnaliseTransicaoMesesService.obter_nome_mes(mes_origem),
                'transicoes': []
            }

            total_transicoes = sum(transicoes[mes_origem].values())

            for mes_destino in range(1, 13):
                freq = transicoes[mes_origem][mes_destino]
                percentual = round((freq / total_transicoes * 100), 2) if total_transicoes > 0 else 0

                linha['transicoes'].append({
                    'mes_destino': mes_destino,
                    'mes_nome': AnaliseTransicaoMesesService.obter_nome_mes(mes_destino),
                    'frequencia': freq,
                    'percentual': percentual
                })

            linha['transicoes'] = sorted(linha['transicoes'], key=lambda x: x['frequencia'], reverse=True)
            matriz.append(linha)

        return matriz

    @staticmethod
    def identificar_sequencias_comuns(sorteios):
        sequencias_2 = defaultdict(int)
        sequencias_3 = defaultdict(int)

        for i in range(len(sorteios) - 1):
            seq_2 = (sorteios[i].mes_sorte, sorteios[i + 1].mes_sorte)
            sequencias_2[seq_2] += 1

        for i in range(len(sorteios) - 2):
            seq_3 = (sorteios[i].mes_sorte, sorteios[i + 1].mes_sorte, sorteios[i + 2].mes_sorte)
            sequencias_3[seq_3] += 1

        resultado = {
            'duplas': [],
            'triplas': []
        }

        for seq, freq in sorted(sequencias_2.items(), key=lambda x: x[1], reverse=True)[:10]:
            resultado['duplas'].append({
                'sequencia': f"{AnaliseTransicaoMesesService.obter_nome_mes(seq[0])} → {AnaliseTransicaoMesesService.obter_nome_mes(seq[1])}",
                'meses': seq,
                'frequencia': freq
            })

        for seq, freq in sorted(sequencias_3.items(), key=lambda x: x[1], reverse=True)[:10]:
            resultado['triplas'].append({
                'sequencia': f"{AnaliseTransicaoMesesService.obter_nome_mes(seq[0])} → {AnaliseTransicaoMesesService.obter_nome_mes(seq[1])} → {AnaliseTransicaoMesesService.obter_nome_mes(seq[2])}",
                'meses': seq,
                'frequencia': freq
            })

        return resultado

    @staticmethod
    def analisar_persistencia(sorteios):
        persistencia = defaultdict(int)

        i = 0
        while i < len(sorteios) - 1:
            mes_atual = sorteios[i].mes_sorte
            contador = 1

            while i + contador < len(sorteios) and sorteios[i + contador].mes_sorte == mes_atual:
                contador += 1

            if contador > 1:
                persistencia[mes_atual] = max(persistencia[mes_atual], contador)

            i += contador

        resultado = []
        for mes, max_repeticoes in sorted(persistencia.items(), key=lambda x: x[1], reverse=True):
            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseTransicaoMesesService.obter_nome_mes(mes),
                'max_repeticoes_consecutivas': max_repeticoes
            })

        return resultado

    @staticmethod
    def calcular_probabilidades_proxima(sorteios):
        if not sorteios:
            return {}

        ultimo_mes = sorteios[-1].mes_sorte
        transicoes = defaultdict(int)

        for i in range(len(sorteios) - 1):
            if sorteios[i].mes_sorte == ultimo_mes:
                transicoes[sorteios[i + 1].mes_sorte] += 1

        total = sum(transicoes.values())
        resultado = []

        for mes, freq in sorted(transicoes.items(), key=lambda x: x[1], reverse=True):
            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseTransicaoMesesService.obter_nome_mes(mes),
                'frequencia': freq,
                'probabilidade': round((freq / total * 100), 2) if total > 0 else 0
            })

        return {
            'ultimo_mes': ultimo_mes,
            'ultimo_mes_nome': AnaliseTransicaoMesesService.obter_nome_mes(ultimo_mes),
            'probabilidades': resultado
        }

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
