from collections import defaultdict, Counter
from models import Sorteio


class AnaliseProbabilidadeCondicionalService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if len(sorteios) < 5:
            return {'erro': 'Dados insuficientes para análise', 'total_concursos': len(sorteios)}

        return {
            'total_concursos': len(sorteios),
            'probabilidade_dezena_dado_mes': AnaliseProbabilidadeCondicionalService.calcular_prob_dezena_dado_mes(sorteios),
            'probabilidade_mes_dada_dezena': AnaliseProbabilidadeCondicionalService.calcular_prob_mes_dada_dezena(sorteios),
            'probabilidade_par_impar_dado_mes': AnaliseProbabilidadeCondicionalService.calcular_prob_par_impar_dado_mes(sorteios),
            'probabilidade_proxima_dezena': AnaliseProbabilidadeCondicionalService.prever_proximas_dezenas(sorteios),
            'probabilidade_proximo_mes': AnaliseProbabilidadeCondicionalService.prever_proximo_mes(sorteios)
        }

    @staticmethod
    def calcular_prob_dezena_dado_mes(sorteios):
        # P(Dezena | Mês) = Frequência de dezena quando o mês aparece
        dezenas_por_mes = defaultdict(lambda: Counter())
        total_por_mes = Counter()

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            total_por_mes[mes] += 1

            for dezena in sorteio.get_posicoes_lista():
                dezenas_por_mes[mes][dezena] += 1

        resultado = []
        for mes in range(1, 13):
            if total_por_mes[mes] == 0:
                continue

            top_dezenas = dezenas_por_mes[mes].most_common(10)

            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseProbabilidadeCondicionalService.obter_nome_mes(mes),
                'total_sorteios': total_por_mes[mes],
                'dezenas_mais_provaveis': [
                    {
                        'dezena': dez,
                        'frequencia': freq,
                        'probabilidade': round((freq / (total_por_mes[mes] * 7) * 100), 2)
                    }
                    for dez, freq in top_dezenas
                ]
            })

        return resultado

    @staticmethod
    def calcular_prob_mes_dada_dezena(sorteios):
        # P(Mês | Dezena) = Frequência de mês quando a dezena aparece
        meses_por_dezena = defaultdict(lambda: Counter())
        total_por_dezena = Counter()

        for sorteio in sorteios:
            mes = sorteio.mes_sorte

            for dezena in sorteio.get_posicoes_lista():
                meses_por_dezena[dezena][mes] += 1
                total_por_dezena[dezena] += 1

        resultado = []
        for dezena in range(1, 32):
            if total_por_dezena[dezena] == 0:
                continue

            top_meses = meses_por_dezena[dezena].most_common(5)

            resultado.append({
                'dezena': dezena,
                'total_aparicoes': total_por_dezena[dezena],
                'meses_mais_provaveis': [
                    {
                        'mes': mes,
                        'mes_nome': AnaliseProbabilidadeCondicionalService.obter_nome_mes(mes),
                        'frequencia': freq,
                        'probabilidade': round((freq / total_por_dezena[dezena] * 100), 2)
                    }
                    for mes, freq in top_meses
                ]
            })

        return sorted(resultado, key=lambda x: x['total_aparicoes'], reverse=True)

    @staticmethod
    def calcular_prob_par_impar_dado_mes(sorteios):
        # P(Par/Ímpar | Mês)
        padroes_por_mes = defaultdict(lambda: Counter())

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = sorteio.get_posicoes_lista()

            pares = sum(1 for n in numeros if n % 2 == 0)
            impares = len(numeros) - pares
            padrao = f"{pares}P-{impares}I"

            padroes_por_mes[mes][padrao] += 1

        resultado = []
        for mes in range(1, 13):
            total_mes = sum(padroes_por_mes[mes].values())
            if total_mes == 0:
                continue

            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseProbabilidadeCondicionalService.obter_nome_mes(mes),
                'total_sorteios': total_mes,
                'padroes': [
                    {
                        'padrao': padrao,
                        'frequencia': freq,
                        'probabilidade': round((freq / total_mes * 100), 2)
                    }
                    for padrao, freq in padroes_por_mes[mes].most_common()
                ]
            })

        return resultado

    @staticmethod
    def prever_proximas_dezenas(sorteios):
        # Baseado nos últimos N sorteios, prevê próximas dezenas
        ultimos_sorteios = sorteios[-20:]

        # Frequência nas últimas 20
        freq_recente = Counter()
        for sorteio in ultimos_sorteios:
            for dezena in sorteio.get_posicoes_lista():
                freq_recente[dezena] += 1

        # Atraso (últimas 20)
        ultimas_aparicoes = {}
        for idx, sorteio in enumerate(ultimos_sorteios):
            for dezena in sorteio.get_posicoes_lista():
                ultimas_aparicoes[dezena] = idx

        atrasos = {}
        for dezena in range(1, 32):
            if dezena in ultimas_aparicoes:
                atrasos[dezena] = len(ultimos_sorteios) - 1 - ultimas_aparicoes[dezena]
            else:
                atrasos[dezena] = len(ultimos_sorteios)

        # Score combinado (frequência alta + atraso moderado)
        scores = []
        for dezena in range(1, 32):
            freq = freq_recente.get(dezena, 0)
            atraso = atrasos.get(dezena, 0)

            # Score: dezenas com frequência média-alta e atraso moderado
            score = (freq * 2) + (atraso * 0.5)

            scores.append({
                'dezena': dezena,
                'frequencia_recente': freq,
                'atraso': atraso,
                'score': round(score, 2)
            })

        return {
            'dezenas_mais_quentes': sorted(scores, key=lambda x: x['frequencia_recente'], reverse=True)[:15],
            'dezenas_mais_atrasadas': sorted(scores, key=lambda x: x['atraso'], reverse=True)[:15],
            'dezenas_por_score': sorted(scores, key=lambda x: x['score'], reverse=True)[:15]
        }

    @staticmethod
    def prever_proximo_mes(sorteios):
        # Baseado no último mês sorteado e transições históricas
        if not sorteios:
            return {}

        ultimo_mes = sorteios[-1].mes_sorte
        transicoes = defaultdict(int)

        for i in range(len(sorteios) - 1):
            if sorteios[i].mes_sorte == ultimo_mes:
                transicoes[sorteios[i + 1].mes_sorte] += 1

        total_transicoes = sum(transicoes.values())

        probabilidades = []
        for mes, freq in transicoes.items():
            probabilidades.append({
                'mes': mes,
                'mes_nome': AnaliseProbabilidadeCondicionalService.obter_nome_mes(mes),
                'frequencia': freq,
                'probabilidade': round((freq / total_transicoes * 100), 2) if total_transicoes > 0 else 0
            })

        return {
            'ultimo_mes': ultimo_mes,
            'ultimo_mes_nome': AnaliseProbabilidadeCondicionalService.obter_nome_mes(ultimo_mes),
            'total_transicoes_historicas': total_transicoes,
            'meses_mais_provaveis': sorted(probabilidades, key=lambda x: x['probabilidade'], reverse=True)
        }

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')
