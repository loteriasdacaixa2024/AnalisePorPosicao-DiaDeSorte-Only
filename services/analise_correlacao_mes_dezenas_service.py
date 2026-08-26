from collections import defaultdict
from models import Sorteio


class AnaliseCorrelacaoMesDezenaService:

    @staticmethod
    def obter_analise_completa():
        sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

        if not sorteios:
            return {'erro': 'Nenhum sorteio encontrado', 'total_concursos': 0}

        return {
            'total_concursos': len(sorteios),
            'dezenas_por_mes': AnaliseCorrelacaoMesDezenaService.analisar_dezenas_por_mes(sorteios),
            'meses_por_dezena': AnaliseCorrelacaoMesDezenaService.analisar_meses_por_dezena(sorteios),
            'combinacoes_fortes': AnaliseCorrelacaoMesDezenaService.identificar_combinacoes_fortes(sorteios),
            'indices_correlacao': AnaliseCorrelacaoMesDezenaService.calcular_indices_correlacao(sorteios)
        }

    @staticmethod
    def analisar_dezenas_por_mes(sorteios):
        dezenas_por_mes = defaultdict(lambda: defaultdict(int))

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                dezenas_por_mes[mes][numero] += 1

        resultado = []
        for mes in range(1, 13):
            top_dezenas = sorted(dezenas_por_mes[mes].items(), key=lambda x: x[1], reverse=True)[:10]

            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseCorrelacaoMesDezenaService.obter_nome_mes(mes),
                'total_sorteios': sum(1 for s in sorteios if s.mes_sorte == mes),
                'top_dezenas': [
                    {
                        'dezena': dez,
                        'frequencia': freq,
                        'percentual': round((freq / max(1, sum(1 for s in sorteios if s.mes_sorte == mes)) * 100), 2)
                    }
                    for dez, freq in top_dezenas
                ]
            })

        return resultado

    @staticmethod
    def analisar_meses_por_dezena(sorteios):
        meses_por_dezena = defaultdict(lambda: defaultdict(int))

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                meses_por_dezena[numero][mes] += 1

        resultado = []
        for dezena in range(1, 32):
            meses_freq = sorted(meses_por_dezena[dezena].items(), key=lambda x: x[1], reverse=True)[:5]

            if meses_freq:
                resultado.append({
                    'dezena': dezena,
                    'top_meses': [
                        {
                            'mes': mes,
                            'mes_nome': AnaliseCorrelacaoMesDezenaService.obter_nome_mes(mes),
                            'frequencia': freq
                        }
                        for mes, freq in meses_freq
                    ]
                })

        return resultado

    @staticmethod
    def identificar_combinacoes_fortes(sorteios):
        combinacoes = defaultdict(int)

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                combinacoes[(mes, numero)] += 1

        resultado = []
        for (mes, dezena), freq in sorted(combinacoes.items(), key=lambda x: x[1], reverse=True)[:20]:
            total_mes = sum(1 for s in sorteios if s.mes_sorte == mes)
            total_dezena = sum(1 for s in sorteios if dezena in s.get_posicoes_lista())

            resultado.append({
                'mes': mes,
                'mes_nome': AnaliseCorrelacaoMesDezenaService.obter_nome_mes(mes),
                'dezena': dezena,
                'frequencia': freq,
                'percentual_no_mes': round((freq / max(1, total_mes) * 100), 2),
                'forca_correlacao': round((freq / max(1, (total_mes * total_dezena / len(sorteios)))) * 100, 2)
            })

        return resultado

    @staticmethod
    def calcular_indices_correlacao(sorteios):
        correlacoes = defaultdict(lambda: {'aparicoes_juntas': 0, 'aparicoes_mes': 0, 'aparicoes_dezena': 0})

        for sorteio in sorteios:
            mes = sorteio.mes_sorte
            numeros = sorteio.get_posicoes_lista()

            for numero in numeros:
                correlacoes[(mes, numero)]['aparicoes_juntas'] += 1

        for mes in range(1, 13):
            total_mes = sum(1 for s in sorteios if s.mes_sorte == mes)
            for dezena in range(1, 32):
                correlacoes[(mes, dezena)]['aparicoes_mes'] = total_mes

        for dezena in range(1, 32):
            total_dezena = sum(1 for s in sorteios if dezena in s.get_posicoes_lista())
            for mes in range(1, 13):
                correlacoes[(mes, dezena)]['aparicoes_dezena'] = total_dezena

        resultado = []
        total_sorteios = len(sorteios)

        for (mes, dezena), dados in correlacoes.items():
            if dados['aparicoes_juntas'] > 0:
                prob_mes = dados['aparicoes_mes'] / total_sorteios
                prob_dezena = dados['aparicoes_dezena'] / total_sorteios
                prob_juntas = dados['aparicoes_juntas'] / total_sorteios
                prob_esperada = prob_mes * prob_dezena

                indice = (prob_juntas / prob_esperada) if prob_esperada > 0 else 0

                if indice > 1.2:
                    resultado.append({
                        'mes': mes,
                        'mes_nome': AnaliseCorrelacaoMesDezenaService.obter_nome_mes(mes),
                        'dezena': dezena,
                        'indice': round(indice, 2),
                        'interpretacao': 'Forte correlação positiva' if indice > 1.5 else 'Correlação positiva moderada'
                    })

        return sorted(resultado, key=lambda x: x['indice'], reverse=True)[:15]

    @staticmethod
    def obter_nome_mes(numero):
        meses = {
            1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
            5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
            9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
        }
        return meses.get(numero, 'Desconhecido')

    @staticmethod
    def resolver_numero_mes(mes_ref):
        """Aceita número 1-12, nome completo ou abreviado (Jan, Fev...)."""
        if mes_ref is None:
            return None
        if isinstance(mes_ref, int) and 1 <= mes_ref <= 12:
            return mes_ref
        texto = str(mes_ref).strip().lower()
        if texto.isdigit():
            n = int(texto)
            return n if 1 <= n <= 12 else None
        mapa = {
            'janeiro': 1, 'jan': 1,
            'fevereiro': 2, 'fev': 2,
            'março': 3, 'marco': 3, 'mar': 3,
            'abril': 4, 'abr': 4,
            'maio': 5, 'mai': 5,
            'junho': 6, 'jun': 6,
            'julho': 7, 'jul': 7,
            'agosto': 8, 'ago': 8,
            'setembro': 9, 'set': 9,
            'outubro': 10, 'out': 10,
            'novembro': 11, 'nov': 11,
            'dezembro': 12, 'dez': 12,
        }
        return mapa.get(texto)

    @staticmethod
    def obter_top_dezenas_do_mes(mes_ref, top=10):
        """Top dezenas que mais saem quando o Mês da Sorte é o informado."""
        mes_num = AnaliseCorrelacaoMesDezenaService.resolver_numero_mes(mes_ref)
        if not mes_num:
            return None

        dados = AnaliseCorrelacaoMesDezenaService.obter_analise_completa()
        if dados.get('erro'):
            return None

        for item in dados.get('dezenas_por_mes', []):
            if item['mes'] == mes_num:
                top_list = item.get('top_dezenas', [])[:top]
                numeros_freq = [t['dezena'] for t in top_list]
                numeros_ordenados = sorted(numeros_freq)
                return {
                    'mes': mes_num,
                    'mes_nome': item['mes_nome'],
                    'total_sorteios': item.get('total_sorteios', 0),
                    'top_dezenas': top_list,
                    'numeros': numeros_freq,
                    'numeros_ordenados': numeros_ordenados,
                    'quantidade': len(numeros_ordenados),
                }
        return None
