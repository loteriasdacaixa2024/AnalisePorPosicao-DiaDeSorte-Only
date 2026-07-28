"""
Serviço de Análise de Finais Iguais - Dia de Sorte
Detecta e analisa ocorrências de dezenas com finais (últimos dígitos) iguais
"""
from models.sorteio import Sorteio
from collections import Counter, defaultdict
from datetime import datetime


class AnaliseFinaisIguaisService:

    @staticmethod
    def analisar_finais_iguais():
        """
        Analisa finais iguais em todos os concursos
        Retorna Top 3, insights e recomendações
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if not sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}

            # Contadores
            finais_counter = Counter()
            finais_por_concurso = []

            for sorteio in sorteios:
                dezenas = sorteio.get_posicoes_lista()
                finais = [str(num)[-1] for num in dezenas]  # Último dígito

                # Contar finais repetidos neste concurso
                finais_repetidos = [final for final, count in Counter(finais).items() if count >= 2]

                for final in finais_repetidos:
                    finais_counter[final] += 1

                finais_por_concurso.append({
                    'concurso': sorteio.concurso,
                    'finais': finais,
                    'repetidos': finais_repetidos
                })

            total_concursos = len(sorteios)

            # Top 3 finais mais frequentes
            top3_finais = []
            for final, count in finais_counter.most_common(3):
                percentual = round((count / total_concursos) * 100, 2)
                top3_finais.append({
                    'label': f'Final {final}',
                    'final': final,
                    'count': count,
                    'pct': percentual
                })

            # Insights
            insights = AnaliseFinaisIguaisService._gerar_insights(
                finais_counter, finais_por_concurso, total_concursos
            )

            # Recomendações
            recomendacoes = AnaliseFinaisIguaisService._gerar_recomendacoes(
                top3_finais, finais_por_concurso
            )

            return {
                'top3': top3_finais,
                'insights': insights,
                'recomendacoes': recomendacoes,
                'total_concursos': total_concursos,
                'total_finais_unicos': len(finais_counter)
            }

        except Exception as e:
            return {'erro': f'Erro ao analisar finais iguais: {str(e)}'}

    @staticmethod
    def _gerar_insights(finais_counter, finais_por_concurso, total_concursos):
        """Gera insights inteligentes sobre finais iguais"""
        insights = []

        # Insight 1: Final mais frequente
        if finais_counter:
            top_final = finais_counter.most_common(1)[0]
            pct = round((top_final[1] / total_concursos) * 100, 2)
            insights.append({
                'title': f'Final {top_final[0]} é o mais frequente',
                'detail': f'Aparece em {top_final[1]} concursos ({pct}% do total)'
            })

        # Insight 2: Tendência nos últimos 10 concursos
        ultimos_10 = finais_por_concurso[-10:]
        finais_recentes = Counter()
        for item in ultimos_10:
            for final in item['repetidos']:
                finais_recentes[final] += 1

        if finais_recentes:
            top_recente = finais_recentes.most_common(1)[0]
            insights.append({
                'title': f'Tendência recente: Final {top_recente[0]}',
                'detail': f'Nos últimos 10 concursos, apareceu {top_recente[1]} vezes com finais repetidos'
            })

        # Insight 3: Média de finais repetidos por concurso
        concursos_com_repeticao = sum(1 for item in finais_por_concurso if item['repetidos'])
        pct_repeticao = round((concursos_com_repeticao / total_concursos) * 100, 2)
        insights.append({
            'title': f'{pct_repeticao}% dos concursos têm finais repetidos',
            'detail': f'{concursos_com_repeticao} de {total_concursos} concursos apresentam pelo menos 2 dezenas com o mesmo final'
        })

        return insights

    @staticmethod
    def _gerar_recomendacoes(top3_finais, finais_por_concurso):
        """Gera recomendações estratégicas"""
        recomendacoes = []

        if top3_finais:
            finais_str = ', '.join([f['final'] for f in top3_finais])
            recomendacoes.append(
                f'Considere incluir dezenas com finais {finais_str} em seus jogos, pois são os mais frequentes'
            )

        recomendacoes.append(
            'Evite concentrar muitas dezenas com o mesmo final em um único jogo'
        )

        recomendacoes.append(
            'Combine finais frequentes com outros filtros (par/ímpar, sequências) para maior equilíbrio'
        )

        recomendacoes.append(
            'Para maximizar cobertura, distribua as dezenas entre diferentes finais'
        )

        return recomendacoes
