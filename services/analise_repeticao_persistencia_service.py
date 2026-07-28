from collections import defaultdict, Counter
from models import Sorteio


class AnaliseRepeticaoPersistenciaService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if len(sorteios) < 2:
            return {'erro': 'Dados insuficientes', 'total_concursos': len(sorteios)}

        return {
            'total_concursos': len(sorteios),
            'repeticoes_consecutivas_dezenas': AnaliseRepeticaoPersistenciaService.analisar_repeticoes_dezenas(sorteios),
            'repeticoes_consecutivas_meses': AnaliseRepeticaoPersistenciaService.analisar_repeticoes_meses(sorteios),
            'persistencia_dezenas': AnaliseRepeticaoPersistenciaService.analisar_persistencia_dezenas(sorteios),
            'persistencia_meses': AnaliseRepeticaoPersistenciaService.analisar_persistencia_meses(sorteios),
            'padroes_repeticao': AnaliseRepeticaoPersistenciaService.identificar_padroes_repeticao(sorteios)
        }

    @staticmethod
    def analisar_repeticoes_dezenas(sorteios):
        repeticoes = []
        contador_repeticoes = defaultdict(int)

        for i in range(len(sorteios) - 1):
            numeros_atual = set(sorteios[i].get_posicoes_lista())
            numeros_seguinte = set(sorteios[i + 1].get_posicoes_lista())

            repetidos = numeros_atual & numeros_seguinte

            if repetidos:
                repeticoes.append({
                    'concurso_atual': sorteios[i].concurso,
                    'concurso_seguinte': sorteios[i + 1].concurso,
                    'dezenas_repetidas': sorted(list(repetidos)),
                    'quantidade': len(repetidos)
                })
                contador_repeticoes[len(repetidos)] += 1

        resultado_contador = []
        total = len(sorteios) - 1

        for qtd, freq in sorted(contador_repeticoes.items(), reverse=True):
            resultado_contador.append({
                'quantidade_repetidas': qtd,
                'frequencia': freq,
                'percentual': round((freq / total * 100), 2)
            })

        return {
            'total_repeticoes': len(repeticoes),
            'percentual_sorteios_com_repeticao': round((len(repeticoes) / total * 100), 2),
            'distribuicao': resultado_contador,
            'ultimas_repeticoes': repeticoes[-10:] if repeticoes else []
        }

    @staticmethod
    def analisar_repeticoes_meses(sorteios):
        repeticoes_consecutivas = 0
        sequencias = []
        sequencia_atual = 1

        for i in range(len(sorteios) - 1):
            if sorteios[i].mes_sorte == sorteios[i + 1].mes_sorte:
                repeticoes_consecutivas += 1
                sequencia_atual += 1
            else:
                if sequencia_atual > 1:
                    sequencias.append({
                        'mes': sorteios[i].mes_sorte,
                        'mes_nome': sorteios[i].get_nome_mes(),
                        'tamanho_sequencia': sequencia_atual,
                        'concurso_final': sorteios[i].concurso
                    })
                sequencia_atual = 1

        return {
            'total_repeticoes': repeticoes_consecutivas,
            'percentual': round((repeticoes_consecutivas / (len(sorteios) - 1) * 100), 2),
            'sequencias_identificadas': sorted(sequencias, key=lambda x: x['tamanho_sequencia'], reverse=True)[:10]
        }

    @staticmethod
    def analisar_persistencia_dezenas(sorteios):
        persistencia = defaultdict(lambda: {'sequencias': [], 'max_sequencia': 0})

        for dezena in range(1, 32):
            sequencia_atual = 0
            sequencias_temp = []

            for sorteio in sorteios:
                if dezena in sorteio.get_posicoes_lista():
                    sequencia_atual += 1
                else:
                    if sequencia_atual > 0:
                        sequencias_temp.append(sequencia_atual)
                    sequencia_atual = 0

            if sequencia_atual > 0:
                sequencias_temp.append(sequencia_atual)

            if sequencias_temp:
                persistencia[dezena]['sequencias'] = sequencias_temp
                persistencia[dezena]['max_sequencia'] = max(sequencias_temp)
                persistencia[dezena]['media_sequencia'] = round(sum(sequencias_temp) / len(sequencias_temp), 2)

        resultado = []
        for dezena, dados in persistencia.items():
            if dados['max_sequencia'] >= 2:
                resultado.append({
                    'dezena': dezena,
                    'max_sequencia': dados['max_sequencia'],
                    'media_sequencia': dados['media_sequencia'],
                    'total_sequencias': len(dados['sequencias'])
                })

        return sorted(resultado, key=lambda x: x['max_sequencia'], reverse=True)[:20]

    @staticmethod
    def analisar_persistencia_meses(sorteios):
        persistencia = defaultdict(lambda: {'sequencias': [], 'max_sequencia': 0})

        for mes in range(1, 13):
            sequencia_atual = 0
            sequencias_temp = []

            for sorteio in sorteios:
                if sorteio.mes_sorte == mes:
                    sequencia_atual += 1
                else:
                    if sequencia_atual > 0:
                        sequencias_temp.append(sequencia_atual)
                    sequencia_atual = 0

            if sequencia_atual > 0:
                sequencias_temp.append(sequencia_atual)

            if sequencias_temp:
                persistencia[mes]['sequencias'] = sequencias_temp
                persistencia[mes]['max_sequencia'] = max(sequencias_temp)
                persistencia[mes]['media_sequencia'] = round(sum(sequencias_temp) / len(sequencias_temp), 2)

        resultado = []
        for mes, dados in persistencia.items():
            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseRepeticaoPersistenciaService.obter_nome_mes(mes),
                'max_sequencia': dados['max_sequencia'],
                'media_sequencia': dados['media_sequencia'],
                'total_sequencias': len(dados['sequencias'])
            })

        return sorted(resultado, key=lambda x: x['max_sequencia'], reverse=True)

    @staticmethod
    def identificar_padroes_repeticao(sorteios):
        padroes_quantidade = Counter()

        for i in range(len(sorteios) - 1):
            numeros_atual = set(sorteios[i].get_posicoes_lista())
            numeros_seguinte = set(sorteios[i + 1].get_posicoes_lista())
            qtd_repetidas = len(numeros_atual & numeros_seguinte)
            padroes_quantidade[qtd_repetidas] += 1

        return {
            'padrao_mais_comum': padroes_quantidade.most_common(1)[0] if padroes_quantidade else (0, 0),
            'distribuicao_completa': dict(padroes_quantidade)
        }

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
