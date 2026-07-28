"""
================================================================================
SERVICE: Análises Sequenciais - DIA DE SORTE
================================================================================
Módulo ISOLADO para análise de sequências de números consecutivos.

RASTREIA:
- Duplas (2 números consecutivos)
- Trios (3 números consecutivos)
- Quádruplas (4 números consecutivos)
- Quíntuplas (5 números consecutivos)

CADA ANÁLISE INCLUI:
- TOP RANKING
- INSIGHTS INTELIGENTES
- RECOMENDAÇÕES ESTRATÉGICAS

Cor Principal: #D4B31A (Dourado Dia de Sorte)

Destino: services/analises_sequenciais_service.py
================================================================================
"""

from collections import Counter
from datetime import datetime

# Importar o modelo Sorteio do projeto (usa SQLAlchemy igual ao resto do sistema)
from models.sorteio import Sorteio, db

# =============================================================================
# SERVICE PRINCIPAL
# =============================================================================

class AnalisesSequenciaisService:
    """Serviço de análises sequenciais (números consecutivos)"""

    @staticmethod
    def _buscar_todos_resultados():
        """Busca todos os resultados do banco de dados usando SQLAlchemy"""
        try:
            # Usar SQLAlchemy igual ao resto do sistema
            resultados = Sorteio.query.order_by(Sorteio.concurso.desc()).all()
            print(f"[DEBUG] Resultados via SQLAlchemy: {len(resultados)}")
            return resultados

        except Exception as e:
            import traceback
            print(f"[ERRO BUSCAR] {e}")
            print(traceback.format_exc())
            return []

    @staticmethod
    def _encontrar_sequencias(numeros):
        """
        Encontra todas as sequências consecutivas em uma lista de números.

        Args:
            numeros: Lista de 7 números sorteados (já ordenados)

        Returns:
            dict: Dicionário com sequências por tamanho (2, 3, 4, 5)
        """
        # Garantir que os números estão ordenados
        nums = sorted(numeros)

        sequencias = {
            2: [],  # Duplas
            3: [],  # Trios
            4: [],  # Quádruplas
            5: [],  # Quíntuplas
        }

        # Encontrar todas as sequências consecutivas
        i = 0
        while i < len(nums):
            # Iniciar uma nova sequência
            seq = [nums[i]]

            # Estender enquanto houver números consecutivos
            j = i + 1
            while j < len(nums) and nums[j] == nums[j-1] + 1:
                seq.append(nums[j])
                j += 1

            # Registrar sequências de tamanho 2 ou mais
            if len(seq) >= 2:
                # Para uma sequência de tamanho N, extraímos todas as sub-sequências
                # Por exemplo: [1,2,3,4] contém:
                # - 3 duplas: (1,2), (2,3), (3,4)
                # - 2 trios: (1,2,3), (2,3,4)
                # - 1 quádrupla: (1,2,3,4)

                for tamanho in [2, 3, 4, 5]:
                    if len(seq) >= tamanho:
                        for k in range(len(seq) - tamanho + 1):
                            sub_seq = tuple(seq[k:k+tamanho])
                            sequencias[tamanho].append(sub_seq)

            i = j if j > i + 1 else i + 1

        return sequencias

    @staticmethod
    def analisar_sequencias():
        """
        Análise COMPLETA de sequências consecutivas.

        Returns:
            dict: Dados completos para o dashboard
        """
        try:
            print("[DEBUG] Iniciando analisar_sequencias...")
            resultados = AnalisesSequenciaisService._buscar_todos_resultados()
            print(f"[DEBUG] Resultados encontrados: {len(resultados) if resultados else 0}")

            if not resultados:
                return {
                    'sucesso': False,
                    'erro': 'Nenhum resultado encontrado no banco de dados'
                }

            # Contadores para cada tamanho de sequência
            contadores = {
                2: Counter(),  # Duplas
                3: Counter(),  # Trios
                4: Counter(),  # Quádruplas
                5: Counter(),  # Quíntuplas
            }

            # Contagem de sorteios que contêm cada tipo de sequência
            sorteios_com_sequencia = {
                2: 0,
                3: 0,
                4: 0,
                5: 0,
            }

            total_sorteios = len(resultados)
            ultimo_concurso = resultados[0].concurso if resultados else 0
            ultima_data = resultados[0].data_sorteio.strftime('%d/%m/%Y') if resultados and resultados[0].data_sorteio else ''

            # Processar cada sorteio
            for resultado in resultados:
                # Usar atributos do modelo SQLAlchemy (não dicionário)
                numeros = [
                    resultado.posicao_1, resultado.posicao_2, resultado.posicao_3,
                    resultado.posicao_4, resultado.posicao_5, resultado.posicao_6,
                    resultado.posicao_7
                ]

                # Encontrar sequências neste sorteio
                sequencias = AnalisesSequenciaisService._encontrar_sequencias(numeros)

                # Contar cada sequência encontrada
                for tamanho in [2, 3, 4, 5]:
                    if sequencias[tamanho]:
                        sorteios_com_sequencia[tamanho] += 1
                        for seq in sequencias[tamanho]:
                            contadores[tamanho][seq] += 1

            # Formatar resultados para cada tamanho
            dados_sequencias = {}

            for tamanho in [2, 3, 4, 5]:
                nome_tipo = {
                    2: 'duplas',
                    3: 'trios',
                    4: 'quadruplas',
                    5: 'quintuplas'
                }[tamanho]

                nome_display = {
                    2: 'Duplas',
                    3: 'Trios',
                    4: 'Quádruplas',
                    5: 'Quíntuplas'
                }[tamanho]

                # TODAS as sequências que já saíram (ordenadas por frequência)
                top_sequencias = contadores[tamanho].most_common()

                # Formatar para exibição
                ranking = []
                for i, (seq, freq) in enumerate(top_sequencias, 1):
                    seq_str = ' - '.join(str(n).zfill(2) for n in seq)
                    percentual = (freq / total_sorteios) * 100

                    ranking.append({
                        'posicao': i,
                        'sequencia': seq_str,
                        'numeros': list(seq),
                        'frequencia': freq,
                        'percentual': round(percentual, 2)
                    })

                # Estatísticas gerais
                total_ocorrencias = sum(contadores[tamanho].values())
                total_unicas = len(contadores[tamanho])
                pct_sorteios = (sorteios_com_sequencia[tamanho] / total_sorteios) * 100 if total_sorteios > 0 else 0

                dados_sequencias[nome_tipo] = {
                    'nome': nome_display,
                    'tamanho': tamanho,
                    'ranking': ranking,
                    'estatisticas': {
                        'total_ocorrencias': total_ocorrencias,
                        'sequencias_unicas': total_unicas,
                        'sorteios_com_sequencia': sorteios_com_sequencia[tamanho],
                        'pct_sorteios': round(pct_sorteios, 2),
                        'media_por_sorteio': round(total_ocorrencias / total_sorteios, 2) if total_sorteios > 0 else 0
                    }
                }

            # Calcular SEQUÊNCIAS FALTANTES
            faltantes = AnalisesSequenciaisService._calcular_sequencias_faltantes(contadores)

            # Gerar INSIGHTS INTELIGENTES
            insights = AnalisesSequenciaisService._gerar_insights(dados_sequencias, total_sorteios)

            # Adicionar insights sobre sequências faltantes
            insights_faltantes = AnalisesSequenciaisService._gerar_insights_faltantes(faltantes)
            insights.extend(insights_faltantes)

            # Gerar RECOMENDAÇÕES ESTRATÉGICAS
            recomendacoes = AnalisesSequenciaisService._gerar_recomendacoes(dados_sequencias)

            # Adicionar recomendações sobre sequências faltantes
            recomendacoes_faltantes = AnalisesSequenciaisService._gerar_recomendacoes_faltantes(faltantes)
            recomendacoes.extend(recomendacoes_faltantes)

            return {
                'sucesso': True,
                'total_sorteios': total_sorteios,
                'ultimo_concurso': ultimo_concurso,
                'ultima_data': ultima_data,
                'sequencias': dados_sequencias,
                'faltantes': faltantes,
                'insights': insights,
                'recomendacoes': recomendacoes,
                'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }

        except Exception as e:
            import traceback
            erro_detalhado = traceback.format_exc()
            print(f"[ERRO ANALISE] {erro_detalhado}")
            return {
                'sucesso': False,
                'erro': str(e),
                'detalhes': erro_detalhado
            }

    @staticmethod
    def _calcular_sequencias_faltantes(contadores):
        """
        Calcula as sequências que NUNCA saíram.

        Dia de Sorte: números de 1 a 31
        - Duplas possíveis: 30 (1-2 até 30-31)
        - Trios possíveis: 29 (1-2-3 até 29-30-31)
        - Quádruplas possíveis: 28 (1-2-3-4 até 28-29-30-31)
        - Quíntuplas possíveis: 27 (1-2-3-4-5 até 27-28-29-30-31)
        """
        NUMERO_MAXIMO = 31
        faltantes = {}

        for tamanho in [2, 3, 4, 5]:
            # Gerar todas as sequências possíveis
            todas_possiveis = set()
            for inicio in range(1, NUMERO_MAXIMO - tamanho + 2):
                seq = tuple(range(inicio, inicio + tamanho))
                todas_possiveis.add(seq)

            # Sequências que já saíram
            ja_sairam = set(contadores[tamanho].keys())

            # Sequências que faltam
            faltam = todas_possiveis - ja_sairam

            # Ordenar por primeiro número
            faltam_ordenadas = sorted(list(faltam), key=lambda x: x[0])

            # Formatar para exibição
            faltantes_formatadas = []
            for seq in faltam_ordenadas:
                seq_str = ' - '.join(str(n).zfill(2) for n in seq)
                faltantes_formatadas.append({
                    'sequencia': seq_str,
                    'numeros': list(seq)
                })

            nome_tipo = {
                2: 'duplas',
                3: 'trios',
                4: 'quadruplas',
                5: 'quintuplas'
            }[tamanho]

            total_possiveis = NUMERO_MAXIMO - tamanho + 1

            faltantes[nome_tipo] = {
                'lista': faltantes_formatadas,
                'total_faltantes': len(faltantes_formatadas),
                'total_possiveis': total_possiveis,
                'total_ja_sairam': total_possiveis - len(faltantes_formatadas),
                'pct_cobertura': round(((total_possiveis - len(faltantes_formatadas)) / total_possiveis) * 100, 2)
            }

        return faltantes

    @staticmethod
    def _gerar_insights(dados_sequencias, total_sorteios):
        """Gera insights inteligentes baseados nos dados"""
        insights = []

        # Insight sobre duplas
        duplas = dados_sequencias.get('duplas', {})
        if duplas.get('ranking'):
            top_dupla = duplas['ranking'][0]
            pct_sorteios = duplas['estatisticas']['pct_sorteios']
            insights.append({
                'icone': '🔥',
                'titulo': 'Dupla Mais Frequente',
                'texto': f"A dupla {top_dupla['sequencia']} é a campeã absoluta com {top_dupla['frequencia']} ocorrências ({top_dupla['percentual']}% dos sorteios)!"
            })
            insights.append({
                'icone': '📊',
                'titulo': 'Duplas em Geral',
                'texto': f"{pct_sorteios}% dos sorteios contêm pelo menos uma dupla de números consecutivos."
            })

        # Insight sobre trios
        trios = dados_sequencias.get('trios', {})
        if trios.get('ranking'):
            top_trio = trios['ranking'][0]
            pct_sorteios = trios['estatisticas']['pct_sorteios']
            insights.append({
                'icone': '🎯',
                'titulo': 'Trio Mais Frequente',
                'texto': f"O trio {top_trio['sequencia']} apareceu {top_trio['frequencia']} vezes nos sorteios!"
            })
            insights.append({
                'icone': '📈',
                'titulo': 'Trios em Geral',
                'texto': f"Aproximadamente {pct_sorteios}% dos sorteios contêm pelo menos um trio consecutivo."
            })

        # Insight sobre quádruplas
        quadruplas = dados_sequencias.get('quadruplas', {})
        if quadruplas.get('ranking') and quadruplas['ranking']:
            total_quad = quadruplas['estatisticas']['total_ocorrencias']
            insights.append({
                'icone': '💎',
                'titulo': 'Quádruplas são Raras',
                'texto': f"Quádruplas consecutivas são eventos mais raros! Foram registradas {total_quad} ocorrências no total."
            })

        # Insight sobre quíntuplas
        quintuplas = dados_sequencias.get('quintuplas', {})
        if quintuplas.get('ranking') and quintuplas['ranking']:
            insights.append({
                'icone': '🌟',
                'titulo': 'Quíntuplas Existem!',
                'texto': f"Sim! Já ocorreram quíntuplas consecutivas! Um evento extremamente raro com {quintuplas['estatisticas']['total_ocorrencias']} ocorrências."
            })
        elif quintuplas:
            insights.append({
                'icone': '🔍',
                'titulo': 'Quíntuplas',
                'texto': "Quíntuplas consecutivas são extremamente raras ou ainda não ocorreram nos sorteios analisados."
            })

        return insights

    @staticmethod
    def _gerar_recomendacoes(dados_sequencias):
        """Gera recomendações estratégicas baseadas nos dados"""
        recomendacoes = []

        # Recomendação baseada nas duplas mais frequentes
        duplas = dados_sequencias.get('duplas', {})
        if duplas.get('ranking') and len(duplas['ranking']) >= 3:
            top3 = [d['sequencia'] for d in duplas['ranking'][:3]]
            recomendacoes.append({
                'icone': '💡',
                'titulo': 'Inclua Duplas Quentes',
                'texto': f"Considere incluir as duplas mais frequentes: {', '.join(top3)}"
            })

        # Recomendação sobre trios
        trios = dados_sequencias.get('trios', {})
        if trios.get('ranking'):
            top_trio = trios['ranking'][0]
            recomendacoes.append({
                'icone': '🎲',
                'titulo': 'Aposte em Trios',
                'texto': f"O trio {top_trio['sequencia']} é estatisticamente favorável com {top_trio['frequencia']} ocorrências!"
            })

        # Recomendação sobre equilíbrio
        recomendacoes.append({
            'icone': '⚖️',
            'titulo': 'Equilíbrio é Chave',
            'texto': "Combine números consecutivos com números espaçados para uma aposta equilibrada."
        })

        # Recomendação sobre quádruplas
        quadruplas = dados_sequencias.get('quadruplas', {})
        if quadruplas.get('ranking'):
            recomendacoes.append({
                'icone': '🍀',
                'titulo': 'Quádruplas para Arriscar',
                'texto': "Quádruplas são raras mas acontecem! Se quiser arriscar, considere incluir uma sequência de 4."
            })

        return recomendacoes

    @staticmethod
    def _gerar_insights_faltantes(faltantes):
        """Gera insights sobre sequências que ainda não saíram"""
        insights = []

        # Insight sobre duplas faltantes
        duplas = faltantes.get('duplas', {})
        if duplas.get('total_faltantes', 0) > 0:
            insights.append({
                'icone': '🎰',
                'titulo': 'Duplas Inéditas',
                'texto': f"Existem {duplas['total_faltantes']} duplas que NUNCA saíram! Cobertura atual: {duplas['pct_cobertura']}% das duplas possíveis."
            })
        elif duplas.get('total_faltantes', 0) == 0:
            insights.append({
                'icone': '✅',
                'titulo': 'Todas as Duplas Saíram!',
                'texto': f"Incrível! Todas as {duplas['total_possiveis']} duplas possíveis já apareceram nos sorteios!"
            })

        # Insight sobre trios faltantes
        trios = faltantes.get('trios', {})
        if trios.get('total_faltantes', 0) > 0:
            insights.append({
                'icone': '🔮',
                'titulo': 'Trios Inéditos',
                'texto': f"Ainda existem {trios['total_faltantes']} trios que nunca apareceram. Oportunidade?"
            })

        # Insight sobre quádruplas faltantes
        quadruplas = faltantes.get('quadruplas', {})
        if quadruplas.get('total_faltantes', 0) > 0:
            insights.append({
                'icone': '💫',
                'titulo': 'Quádruplas Inéditas',
                'texto': f"{quadruplas['total_faltantes']} quádruplas ainda aguardam sua primeira aparição!"
            })

        # Insight sobre quíntuplas faltantes
        quintuplas = faltantes.get('quintuplas', {})
        if quintuplas.get('total_faltantes', 0) > 0:
            insights.append({
                'icone': '🌠',
                'titulo': 'Quíntuplas Inéditas',
                'texto': f"{quintuplas['total_faltantes']} de {quintuplas['total_possiveis']} quíntuplas possíveis ainda não saíram!"
            })

        return insights

    @staticmethod
    def _gerar_recomendacoes_faltantes(faltantes):
        """Gera recomendações baseadas nas sequências faltantes"""
        recomendacoes = []

        # Recomendação sobre duplas faltantes
        duplas = faltantes.get('duplas', {})
        if duplas.get('lista') and len(duplas['lista']) > 0:
            primeiras = duplas['lista'][:3]
            seqs_str = ', '.join([d['sequencia'] for d in primeiras])
            recomendacoes.append({
                'icone': '🎯',
                'titulo': 'Duplas Inéditas para Arriscar',
                'texto': f"Estas duplas nunca saíram: {seqs_str}. Pode ser a hora delas!"
            })

        # Recomendação sobre trios faltantes
        trios = faltantes.get('trios', {})
        if trios.get('lista') and len(trios['lista']) > 0:
            primeiros = trios['lista'][:2]
            seqs_str = ', '.join([t['sequencia'] for t in primeiros])
            recomendacoes.append({
                'icone': '🎲',
                'titulo': 'Trios Inéditos',
                'texto': f"Os trios {seqs_str} ainda não apareceram. Vale a tentativa!"
            })

        # Recomendação geral
        recomendacoes.append({
            'icone': '🧠',
            'titulo': 'Estratégia das Faltantes',
            'texto': "Sequências inéditas podem representar oportunidades estatísticas. Considere incluí-las em suas apostas!"
        })

        return recomendacoes

    @staticmethod
    def obter_ultimo_concurso():
        """Retorna o número do último concurso para verificar atualizações"""
        try:
            # Usar SQLAlchemy igual ao resto do sistema
            from sqlalchemy import func
            resultado = db.session.query(func.max(Sorteio.concurso)).scalar()
            return resultado if resultado else 0
        except:
            return 0

    @staticmethod
    def obter_status():
        """Retorna status do serviço"""
        try:
            # Usar SQLAlchemy igual ao resto do sistema
            from sqlalchemy import func
            total = db.session.query(func.count(Sorteio.id)).scalar()
            ultimo = db.session.query(func.max(Sorteio.concurso)).scalar()

            return {
                'sucesso': True,
                'status': 'online',
                'total_sorteios': total,
                'ultimo_concurso': ultimo,
                'atualizado_em': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            }
        except Exception as e:
            return {
                'sucesso': False,
                'status': 'erro',
                'erro': str(e)
            }
