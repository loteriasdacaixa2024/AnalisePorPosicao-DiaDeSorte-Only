from collections import defaultdict, Counter
from models import Sorteio


class AnaliseAcumulosMesService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'acumulos_por_mes': AnaliseAcumulosMesService.analisar_acumulos_por_mes(sorteios),
            'sequencias_acumulo': AnaliseAcumulosMesService.identificar_sequencias_acumulo(sorteios),
            'meses_com_maior_acumulo': AnaliseAcumulosMesService.rankear_meses_acumulo(sorteios),
            'relacao_acumulo_valor_proximo': AnaliseAcumulosMesService.analisar_relacao_acumulo_premio(sorteios),
            'tendencias_acumulo': AnaliseAcumulosMesService.analisar_tendencias(sorteios)
        }

    @staticmethod
    def analisar_acumulos_por_mes(sorteios):
        acumulos_por_mes = defaultdict(lambda: {'total': 0, 'acumulou': 0, 'percentual': 0})

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            acumulos_por_mes[mes]['total'] += 1

            if sorteio.ganhadores_7_acertos == 0:
                acumulos_por_mes[mes]['acumulou'] += 1

        resultado = []
        for mes in range(1, 13):
            dados = acumulos_por_mes[mes]
            if dados['total'] > 0:
                dados['percentual'] = round((dados['acumulou'] / dados['total'] * 100), 2)

            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseAcumulosMesService.obter_nome_mes(mes),
                'total_sorteios': dados['total'],
                'total_acumulos': dados['acumulou'],
                'percentual_acumulo': dados['percentual']
            })

        return sorted(resultado, key=lambda x: x['percentual_acumulo'], reverse=True)

    @staticmethod
    def identificar_sequencias_acumulo(sorteios):
        sequencias = []
        sequencia_atual = []

        for sorteio in sorteios:
            if sorteio.ganhadores_7_acertos == 0:
                sequencia_atual.append({
                    'concurso': sorteio.concurso,
                    'mes': sorteio.mes_sorte,
                    'mes_nome': sorteio.get_nome_mes()
                })
            else:
                if len(sequencia_atual) > 1:
                    sequencias.append({
                        'tamanho': len(sequencia_atual),
                        'concursos': [s['concurso'] for s in sequencia_atual],
                        'meses': [s['mes_nome'] for s in sequencia_atual],
                        'inicio': sequencia_atual[0]['concurso'],
                        'fim': sequencia_atual[-1]['concurso']
                    })
                sequencia_atual = []

        # Adiciona última sequência se ainda estiver acumulando
        if len(sequencia_atual) > 1:
            sequencias.append({
                'tamanho': len(sequencia_atual),
                'concursos': [s['concurso'] for s in sequencia_atual],
                'meses': [s['mes_nome'] for s in sequencia_atual],
                'inicio': sequencia_atual[0]['concurso'],
                'fim': sequencia_atual[-1]['concurso']
            })

        return {
            'total_sequencias': len(sequencias),
            'maior_sequencia': max(sequencias, key=lambda x: x['tamanho']) if sequencias else None,
            'top_10_sequencias': sorted(sequencias, key=lambda x: x['tamanho'], reverse=True)[:10]
        }

    @staticmethod
    def rankear_meses_acumulo(sorteios):
        meses_quando_acumulou = Counter()
        meses_quando_premiou = Counter()

        for sorteio in sorteios:
            if sorteio.ganhadores_7_acertos == 0:
                meses_quando_acumulou[sorteio.mes_sorte] += 1
            else:
                meses_quando_premiou[sorteio.mes_sorte] += 1

        resultado_acumulo = []
        resultado_premio = []

        for mes, freq in meses_quando_acumulou.most_common():
            resultado_acumulo.append({
                'mes': mes,
                'mes_nome': AnaliseAcumulosMesService.obter_nome_mes(mes),
                'frequencia': freq
            })

        for mes, freq in meses_quando_premiou.most_common():
            resultado_premio.append({
                'mes': mes,
                'mes_nome': AnaliseAcumulosMesService.obter_nome_mes(mes),
                'frequencia': freq
            })

        return {
            'meses_que_mais_acumularam': resultado_acumulo,
            'meses_que_mais_premiaram': resultado_premio
        }

    @staticmethod
    def analisar_relacao_acumulo_premio(sorteios):
        relacao = []

        for i in range(len(sorteios) - 1):
            sorteio_atual = sorteios[i]
            sorteio_seguinte = sorteios[i + 1]

            if sorteio_atual.ganhadores_7_acertos == 0:
                relacao.append({
                    'concurso_acumulado': sorteio_atual.concurso,
                    'mes_acumulado': sorteio_atual.mes_sorte,
                    'mes_acumulado_nome': sorteio_atual.get_nome_mes(),
                    'concurso_seguinte': sorteio_seguinte.concurso,
                    'mes_seguinte': sorteio_seguinte.mes_sorte,
                    'mes_seguinte_nome': sorteio_seguinte.get_nome_mes(),
                    'premiou_seguinte': sorteio_seguinte.ganhadores_7_acertos > 0
                })

        # Analisa transições
        transicoes_mes = defaultdict(lambda: {'total': 0, 'premiou': 0})

        for r in relacao:
            chave = f"{r['mes_acumulado_nome']} → {r['mes_seguinte_nome']}"
            transicoes_mes[chave]['total'] += 1
            if r['premiou_seguinte']:
                transicoes_mes[chave]['premiou'] += 1

        resultado_transicoes = []
        for transicao, dados in transicoes_mes.items():
            if dados['total'] >= 3:
                resultado_transicoes.append({
                    'transicao': transicao,
                    'total_ocorrencias': dados['total'],
                    'premiou_seguinte': dados['premiou'],
                    'percentual_premio': round((dados['premiou'] / dados['total'] * 100), 2)
                })

        return {
            'total_analises': len(relacao),
            'transicoes_relevantes': sorted(resultado_transicoes, key=lambda x: x['total_ocorrencias'], reverse=True)[:15],
            'ultimas_20_relacoes': relacao[-20:]
        }

    @staticmethod
    def analisar_tendencias(sorteios):
        # Analisa se acúmulos têm tendência a continuar ou parar
        acumulou_e_acumulou = 0
        acumulou_e_premiou = 0
        premiou_e_acumulou = 0
        premiou_e_premiou = 0

        for i in range(len(sorteios) - 1):
            atual_acumulou = sorteios[i].ganhadores_7_acertos == 0
            seguinte_acumulou = sorteios[i + 1].ganhadores_7_acertos == 0

            if atual_acumulou and seguinte_acumulou:
                acumulou_e_acumulou += 1
            elif atual_acumulou and not seguinte_acumulou:
                acumulou_e_premiou += 1
            elif not atual_acumulou and seguinte_acumulou:
                premiou_e_acumulou += 1
            else:
                premiou_e_premiou += 1

        total = len(sorteios) - 1

        return {
            'acumulou_e_acumulou': {
                'quantidade': acumulou_e_acumulou,
                'percentual': round((acumulou_e_acumulou / total * 100), 2)
            },
            'acumulou_e_premiou': {
                'quantidade': acumulou_e_premiou,
                'percentual': round((acumulou_e_premiou / total * 100), 2)
            },
            'premiou_e_acumulou': {
                'quantidade': premiou_e_acumulou,
                'percentual': round((premiou_e_acumulou / total * 100), 2)
            },
            'premiou_e_premiou': {
                'quantidade': premiou_e_premiou,
                'percentual': round((premiou_e_premiou / total * 100), 2)
            }
        }

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
