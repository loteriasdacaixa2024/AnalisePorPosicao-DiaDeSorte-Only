"""
Serviço de Análise de Repetição do Concurso Anterior - Dia de Sorte
Verifica quantas dezenas se repetem do concurso anterior
"""
from models.sorteio import Sorteio
from collections import Counter, defaultdict


class AnaliseRepeticaoConcursoAnteriorService:

    @staticmethod
    def analisar_repeticoes():
        """
        Analisa repetições de dezenas do concurso anterior
        Retorna Top 3, insights e recomendações
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if len(sorteios) < 2:
                return {'erro': 'Dados insuficientes para análise'}

            # Contadores
            dezenas_repetidas_counter = Counter()
            qtd_repeticoes_por_concurso = []
            historico_repeticoes = []

            for i in range(1, len(sorteios)):
                anterior = set(sorteios[i-1].get_posicoes_lista())
                atual = set(sorteios[i].get_posicoes_lista())

                # Dezenas que se repetiram
                repeticoes = anterior.intersection(atual)
                qtd_repeticoes = len(repeticoes)

                qtd_repeticoes_por_concurso.append(qtd_repeticoes)

                for dezena in repeticoes:
                    dezenas_repetidas_counter[dezena] += 1

                historico_repeticoes.append({
                    'concurso': sorteios[i].concurso,
                    'qtd_repeticoes': qtd_repeticoes,
                    'dezenas_repetidas': list(repeticoes)
                })

            total_concursos = len(sorteios) - 1

            # Top 3 dezenas que mais se repetem
            top3_dezenas = []
            for dezena, count in dezenas_repetidas_counter.most_common(3):
                percentual = round((count / total_concursos) * 100, 2)
                top3_dezenas.append({
                    'label': f'Dezena {dezena:02d}',
                    'dezena': dezena,
                    'count': count,
                    'pct': percentual
                })

            # Insights
            insights = AnaliseRepeticaoConcursoAnteriorService._gerar_insights(
                qtd_repeticoes_por_concurso, historico_repeticoes, total_concursos
            )

            # Recomendações
            recomendacoes = AnaliseRepeticaoConcursoAnteriorService._gerar_recomendacoes(
                top3_dezenas, qtd_repeticoes_por_concurso
            )

            return {
                'top3': top3_dezenas,
                'insights': insights,
                'recomendacoes': recomendacoes,
                'total_concursos_analisados': total_concursos,
                'media_repeticoes': round(sum(qtd_repeticoes_por_concurso) / len(qtd_repeticoes_por_concurso), 2)
            }

        except Exception as e:
            return {'erro': f'Erro ao analisar repetições: {str(e)}'}

    @staticmethod
    def _gerar_insights(qtd_repeticoes_por_concurso, historico_repeticoes, total_concursos):
        """Gera insights inteligentes sobre repetições"""
        insights = []

        # Insight 1: Média de repetições
        media_repeticoes = round(sum(qtd_repeticoes_por_concurso) / len(qtd_repeticoes_por_concurso), 2)
        insights.append({
            'title': f'Média de {media_repeticoes} dezenas se repetem',
            'detail': f'Em média, {media_repeticoes} dezenas do concurso anterior aparecem no próximo'
        })

        # Insight 2: Tendência nos últimos 10 concursos
        ultimos_10 = qtd_repeticoes_por_concurso[-10:]
        media_recente = round(sum(ultimos_10) / len(ultimos_10), 2)
        insights.append({
            'title': f'Tendência recente: {media_recente} repetições',
            'detail': f'Nos últimos 10 concursos, a média de repetições é {media_recente}'
        })

        # Insight 3: Concursos sem repetição
        sem_repeticao = qtd_repeticoes_por_concurso.count(0)
        pct_sem_repeticao = round((sem_repeticao / total_concursos) * 100, 2)
        insights.append({
            'title': f'{pct_sem_repeticao}% dos concursos não têm repetição',
            'detail': f'{sem_repeticao} de {total_concursos} concursos não repetiram nenhuma dezena do anterior'
        })

        return insights

    @staticmethod
    def _gerar_recomendacoes(top3_dezenas, qtd_repeticoes_por_concurso):
        """Gera recomendações estratégicas"""
        recomendacoes = []

        media_repeticoes = round(sum(qtd_repeticoes_por_concurso) / len(qtd_repeticoes_por_concurso), 2)

        if top3_dezenas:
            dezenas_str = ', '.join([f"{d['dezena']:02d}" for d in top3_dezenas])
            recomendacoes.append(
                f'As dezenas {dezenas_str} são as que mais se repetem do concurso anterior'
            )

        recomendacoes.append(
            f'Considere incluir cerca de {int(media_repeticoes)} dezenas do último sorteio em seus jogos'
        )

        recomendacoes.append(
            'Não base todo o jogo apenas em repetições - combine com outras estratégias'
        )

        if media_repeticoes >= 2:
            recomendacoes.append(
                'A tendência histórica mostra que pelo menos 2 dezenas costumam se repetir'
            )

        return recomendacoes
