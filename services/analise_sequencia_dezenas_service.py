"""
Serviço de Análise de Sequências de Dezenas - Dia de Sorte
Detecta e analisa sequências (números consecutivos) nos sorteios
"""
from models.sorteio import Sorteio
from collections import Counter, defaultdict


class AnaliseSequenciaDezenasService:

    @staticmethod
    def analisar_sequencias():
        """
        Analisa sequências de dezenas consecutivas
        Retorna Top 3, insights e recomendações
        """
        try:
            sorteios = Sorteio.query.order_by(Sorteio.concurso.asc()).all()

            if not sorteios:
                return {'erro': 'Nenhum sorteio encontrado'}

            # Contadores
            sequencias_counter = defaultdict(int)
            tipos_sequencia = Counter()
            concursos_com_sequencia = []

            for sorteio in sorteios:
                dezenas = sorted(sorteio.get_posicoes_lista())
                sequencias = AnaliseSequenciaDezenasService._detectar_sequencias(dezenas)

                if sequencias:
                    concursos_com_sequencia.append({
                        'concurso': sorteio.concurso,
                        'sequencias': sequencias
                    })

                    for seq in sequencias:
                        tamanho = len(seq)
                        tipos_sequencia[f'Sequência de {tamanho}'] += 1
                        seq_str = '-'.join(map(str, seq))
                        sequencias_counter[seq_str] += 1

            total_concursos = len(sorteios)

            # Top 3 sequências mais frequentes
            top3_sequencias = []
            for seq_str, count in sorted(sequencias_counter.items(), key=lambda x: x[1], reverse=True)[:3]:
                percentual = round((count / total_concursos) * 100, 2)
                top3_sequencias.append({
                    'label': seq_str,
                    'sequencia': seq_str,
                    'count': count,
                    'pct': percentual
                })

            # Insights
            insights = AnaliseSequenciaDezenasService._gerar_insights(
                tipos_sequencia, concursos_com_sequencia, total_concursos
            )

            # Recomendações
            recomendacoes = AnaliseSequenciaDezenasService._gerar_recomendacoes(
                top3_sequencias, tipos_sequencia
            )

            return {
                'top3': top3_sequencias,
                'insights': insights,
                'recomendacoes': recomendacoes,
                'total_concursos': total_concursos,
                'total_com_sequencia': len(concursos_com_sequencia)
            }

        except Exception as e:
            return {'erro': f'Erro ao analisar sequências: {str(e)}'}

    @staticmethod
    def _detectar_sequencias(dezenas):
        """Detecta sequências de números consecutivos"""
        sequencias = []
        sequencia_atual = [dezenas[0]]

        for i in range(1, len(dezenas)):
            if dezenas[i] == dezenas[i-1] + 1:
                sequencia_atual.append(dezenas[i])
            else:
                if len(sequencia_atual) >= 2:
                    sequencias.append(sequencia_atual[:])
                sequencia_atual = [dezenas[i]]

        if len(sequencia_atual) >= 2:
            sequencias.append(sequencia_atual)

        return sequencias

    @staticmethod
    def _gerar_insights(tipos_sequencia, concursos_com_sequencia, total_concursos):
        """Gera insights inteligentes sobre sequências"""
        insights = []

        # Insight 1: Percentual de concursos com sequências
        pct_com_seq = round((len(concursos_com_sequencia) / total_concursos) * 100, 2)
        insights.append({
            'title': f'{pct_com_seq}% dos concursos têm sequências',
            'detail': f'{len(concursos_com_sequencia)} de {total_concursos} concursos apresentam pelo menos uma sequência'
        })

        # Insight 2: Tipo de sequência mais comum
        if tipos_sequencia:
            tipo_mais_comum = tipos_sequencia.most_common(1)[0]
            insights.append({
                'title': f'{tipo_mais_comum[0]} é a mais comum',
                'detail': f'Aparece em {tipo_mais_comum[1]} concursos'
            })

        # Insight 3: Tendência recente
        ultimos_10 = concursos_com_sequencia[-10:] if len(concursos_com_sequencia) >= 10 else concursos_com_sequencia
        if ultimos_10:
            total_seq_recentes = sum(len(c['sequencias']) for c in ultimos_10)
            media_seq = round(total_seq_recentes / len(ultimos_10), 2)
            insights.append({
                'title': f'Média de {media_seq} sequências nos últimos 10 concursos',
                'detail': 'Tendência mostra presença consistente de sequências'
            })

        return insights

    @staticmethod
    def _gerar_recomendacoes(top3_sequencias, tipos_sequencia):
        """Gera recomendações estratégicas"""
        recomendacoes = []

        if top3_sequencias:
            recomendacoes.append(
                'Considere incluir sequências de 2 ou 3 números consecutivos em seus jogos'
            )

        recomendacoes.append(
            'Evite jogos sem nenhuma sequência, pois estatisticamente são menos frequentes'
        )

        recomendacoes.append(
            'Combine sequências com números espaçados para balancear o jogo'
        )

        if 'Sequência de 2' in tipos_sequencia:
            recomendacoes.append(
                'Sequências de 2 números são as mais comuns - inclua pelo menos uma no seu jogo'
            )

        return recomendacoes
